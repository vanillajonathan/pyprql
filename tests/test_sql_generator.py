# -*- coding: utf-8 -*-
import sqlite3
import unittest
from pathlib import Path

from pyprql.lang import prql


class TestSqlGenerator(unittest.TestCase):
    def setUpClass() -> None:
        # Use Path for robust construction, but sqlite3 py3.6 requires str
        db_path = str(Path("tests", "../resources/employee.db"))
        TestSqlGenerator.con = sqlite3.connect(db_path)
        TestSqlGenerator.cur = TestSqlGenerator.con.cursor()

    def run_query(self, text, expected=None):
        # print(text.replace('\n\n', '\n'))
        # print('-' * 40)
        sql = prql.to_sql(text)
        # print(sql)

        rows = TestSqlGenerator.cur.execute(sql)
        columns = [d[0] for d in rows.description]
        # print(f'Columns: {columns}')
        rows = rows.fetchall()
        if expected is not None:
            assert len(rows) == expected

    def test_select_all(self):
        q = """
        from table
        """
        res = prql.to_sql(q)
        self.assertTrue(res.startswith("SELECT * FROM `table`"))
        self.run_query(q)

    def test_select_one(self):
        q = """
        from table | select foo
        """
        res = prql.to_sql(q)
        self.assertTrue(res.startswith("SELECT foo"))
        self.run_query(q)

    def test_sort(self):
        q = """
        from table | select foo | sort foo 
        """
        res = prql.to_sql(q)
        self.assertTrue(res.startswith("SELECT foo"))
        self.run_query(q)

    def test_sort_and_order(self):
        q = """
        from table | select foo | sort foo order:desc 
        """
        res = prql.to_sql(q)
        # print(res)
        self.assertTrue(res.index("ORDER BY foo DESC ") != -1)
        self.run_query(q)

    def test_sort_and_order_2(self):
        q = """
        from table | select foo | sort bar order:asc 
        """
        res = prql.to_sql(q)
        # print(res)
        self.assertTrue(res.index("ORDER BY bar ASC ") != -1)
        self.run_query(q)

    def test_sort_on_many(self):
        q = """
        from table | select foo | sort [ foo, bar ] 
        """
        res = prql.to_sql(q)
        # print(res)
        self.assertTrue(res.index("ORDER BY foo,bar ") != -1)
        self.run_query(q)

    def test_sort_order_on_either_side(self):
        q = """
        from table | select foo | sort order:desc foo order:asc | take 10
        """
        res = prql.to_sql(q)
        print(res)
        assert res.index("ORDER BY foo DESC") != -1


    def test_sort_on_many_with_direction(self):
        q = """
        from table | select foo | sort [ foo, bar ] order:desc 
        """
        res = prql.to_sql(q)
        # print(res)
        self.assertTrue(res.index("ORDER BY foo,bar DESC") != -1)
        self.run_query(q)

    def test_select_two(self):
        q = """
        from table | select [ foo, bar ]
        """
        res = prql.to_sql(q)
        self.assertTrue(res.startswith("SELECT foo,bar"))
        self.run_query(q)

    def test_select_as(self):
        q = """
        from table | select [ foo | as float ,  bar | as string ]
        """
        res = prql.to_sql(q)
        # print(res)
        self.assertTrue(res.startswith("SELECT CAST(foo as float),CAST(bar as string)"))
        self.run_query(q)

    def test_select_as_single(self):
        q = """
        from table | select [ foo | as float  ]
        """
        res = prql.to_sql(q)
        # print(res)
        self.assertTrue(res.startswith("SELECT CAST(foo as float)"))
        self.run_query(q)

    def test_select_as_single_no_brackets_will_fail(self):
        q = """
        from table | select foo | as float
        """
        try:
            res = prql.to_sql(q)
            # print(res)
            self.assertTrue(res.startswith("SELECT CAST(foo as float)"))
            self.run_query(q)
        except Exception as e:
            self.assertTrue(True)

    def test_take(self):
        q = "from table | take 10"
        res = prql.to_sql(q)
        self.assertTrue(res.index("LIMIT 10") != -1)
        self.run_query(q, 10)

    def test_take_with_offset(self):
        q = "from table | take 10 offset:10 "
        res = prql.to_sql(q)
        # print(res)
        self.assertTrue(res.index("LIMIT 10 OFFSET 10") != -1)
        self.run_query(q, 2)

    def test_take_with_offset_2(self):
        q = "from table | take 2 offset:10 "
        res = prql.to_sql(q)
        # print(res)
        self.assertTrue(res.index("LIMIT 2 OFFSET 10") != -1)
        self.run_query(q, 2)

    def test_limit(self):
        q = "from table | take 10"
        res = prql.to_sql(q)
        self.assertTrue(res.index("LIMIT 10") != -1)
        self.run_query(q, 10)

    def test_order_by(self):
        q = "from table | sort country | take 7"
        res = prql.to_sql(q)
        self.assertTrue(res.index("ORDER BY country") != -1)
        self.run_query(q, 7)

    def test_order_by_asc(self):
        q = "from table | sort country order:asc | take 10"
        res = prql.to_sql(q)
        # print(res)
        self.assertTrue(res.index("ORDER BY country ASC") != -1)
        self.run_query(q, 10)

    def test_order_by_desc(self):
        q = "from table | sort country order:desc | take 11"
        res = prql.to_sql(q)
        self.assertTrue(res.index("ORDER BY country DESC") != -1)
        self.run_query(q, 11)

    def test_order_by_invalid_throws_exception(self):
        q = "from table | sort country order:invalid | take 7"
        try:
            res = prql.to_sql(q)

            self.assertTrue(res.index("ORDER BY country INVALID") == -1)
            self.run_query(q, 7)
        except Exception as e:
            self.assertTrue(True)

    def test_join_syntax(self):
        q = """
        from table
        join table2 [id=id]
        """
        res = prql.to_sql(q)
        self.assertTrue(
            res.index("JOIN table2 table2_t ON table_t.id = table2_t.id") != -1
        )
        self.run_query(q, 6)

    def test_join_syntax_2(self):
        q = """
        from table
        join table2 [table.id=table2.id]
        """
        res = prql.to_sql(q)
        # print(res)
        self.assertTrue(
            res.index("JOIN table2 table2_t ON table_t.id = table2_t.id") != -1
        )
        self.run_query(q, 6)

    def test_double_join_syntax_2(self):
        q = """
        from table
        join side:inner table2 [table.id=table2.id]
        """
        res = prql.to_sql(q)
        # print(res)
        self.assertTrue(
            res.index("JOIN table2 table2_t ON table_t.id = table2_t.id") != -1
        )
        self.run_query(q, 6)

    def test_inner_join_syntax_1(self):
        q = """
        from table
        join side:inner table2 [table.id=table2.id]
        """
        res = prql.to_sql(q)
        # print(res)
        self.assertTrue(
            res.index("INNER JOIN table2 table2_t ON table_t.id = table2_t.id") != -1
        )
        self.run_query(q, 6)

    def test_left_join_syntax_1(self):
        q = """
        from table
        join side:left table2 [table.id=table2.id]
        """
        res = prql.to_sql(q)
        # print(res)
        self.assertTrue(
            res.index("LEFT JOIN table2 table2_t ON table_t.id = table2_t.id") != -1
        )
        self.run_query(q, 12)

    def test_right_join_syntax_1(self):
        q = """
        from table
        join side:right table2 [table.id=table2.id]
        """
        res = prql.to_sql(q)
        # print(res)
        self.assertTrue(
            res.index("RIGHT JOIN table2 table2_t ON table_t.id = table2_t.id") != -1
        )

        # This fails beacuse SQLITE doesnt support RIGHT and FULL OUTTER
        # self.run_query(q, 6)

    def test_group_by_single_item_array(self):
        q = """
        from table
        select [ foo, bar ]
        aggregate by:[code] [
            sum price
        ]
        """
        res = prql.to_sql(q)

        self.assertTrue(res.index("SUM(price)") != -1)
        self.assertTrue(res.index("GROUP BY code") != -1)
        self.run_query(q, 3)

    def test_group_by_double_item_array(self):
        q = """
        from table
        select [ foo, bar ]
        aggregate by:[code,country] [
            sum price
        ]
        """
        res = prql.to_sql(q)

        self.assertTrue(res.index("SUM(price)") != -1)
        self.assertTrue(res.index("GROUP BY code,country") != -1)
        self.run_query(q, 5)

    def test_groupby_single_argument(self):
        q = """
        from table
        select [ foo, bar ]
        aggregate by:code [
            sum price
        ]
        """
        res = prql.to_sql(q)

        self.assertTrue(res.index("SUM(price)") != -1)
        self.assertTrue(res.index("GROUP BY code") != -1)
        self.run_query(q, 3)

    def test_named_aggs(self):
        q = """
        from table
        select [ foo, bar ]
        aggregate by:code [
            all_costs: sum price
        ]
        """
        res = prql.to_sql(q)

        self.assertTrue(res.index("SUM(price) as all_costs") != -1)
        self.assertTrue(res.index("GROUP BY code") != -1)
        self.run_query(q, 3)

    def test_derive_syntax(self):
        q = """
        from table
        derive [
         foo_bar: foo + bar
        ]
        """
        res = prql.to_sql(q)
        self.assertTrue(res.index("foo+bar as foo_bar") != -1)
        self.run_query(q, 12)
        # print(res)

    def test_derive_single_column(self):
        q = """
        from table
        derive [
         foo_only: foo
        ]"""
        res = prql.to_sql(q)
        # print(res)
        self.assertTrue(res.index("foo as foo_only") != -1)
        self.run_query(q, 12)

    # @pytest.mark.skip(reason="In Progress")
    def test_derive_single_column_nested(self):
        q = """
        from table
        derive [
         foo_only: table.foo
        ]"""
        res = prql.to_sql(q)
        # print(res)
        self.assertTrue(res.index("foo as foo_only") != -1)
        self.run_query(q, 12)

    def test_filter_where_only(self):
        q = """
        from table
        filter foo > 10
        """
        res = prql.to_sql(q)
        assert res.index("WHERE foo>10") != -1

    # print(res)

    def test_filter_where_multi(self):
        q = """
        from table
        filter [ foo > 10, bar < 20 ]
        """
        res = prql.to_sql(q)
        assert res.index("WHERE foo>10") != -1

    # print(res)

    def test_filter_fstring(self):
        q = """
        from table
        filter s"foo > 10"
        """
        res = prql.to_sql(q)
        # print(res)
        assert res.index("WHERE foo > 10") != -1

    # print(res)

    def test_having(self):
        q = """
                 from employees
                 filter country = "USA"                           # Each line transforms the previous result.
                 derive [                                         # This adds columns / variables.
                   gross_salary: salary + payroll_tax,
                   gross_cost:   gross_salary + benefits_cost     # Variables can use other variables.
                 ]
                 filter gross_cost > 0
                 aggregate by:[title, country] [                  # `by` are the columns to group by.
                     average salary,                              # These are aggregation calcs run on each group.
                     sum     salary,
                     average gross_salary,
                     sum     gross_salary,
                     average gross_cost,
                     sum_gross_cost: sum gross_cost,
                     row_count: count salary
                 ]
                 sort sum_gross_cost
                 filter row_count > 200
                 take 20"""
        res = prql.to_sql(q)
        # print(res)
        assert res.index("HAVING row_count>200") != -1

    # print(res)

    def test_like(self):
        q = '''
        from table
        filter foo | like "bar"'''
        res = prql.to_sql(q)
        # print(res)
        assert res.index('WHERE foo LIKE "bar"') != -1

    # print(res)

    def test_like(self):
        q = '''
        from table
        filter foo | like "%"'''
        res = prql.to_sql(q,True)
        # print(res)
        assert res.index('WHERE foo LIKE "%"') != -1

    # print(res)

    def test_alias(self):
        q = '''
        from e:employees
        derive [
            foo: e.foo
        ]
        '''
        print(q)
        res = prql.to_sql(q)
        assert res.index('FROM `employees` e ') != -1

    # print(res)

    def test_alias_goes_the_extra_mile(self):
        q = '''
        from even_longer_foo:foo
        derive [
            val: foo.some_value,
            other_val: even_longer_foo.other_value
        ]
        '''
        print(q)
        res = prql.to_sql(q)
        # print(res)
        assert res.index('even_longer_foo.some_value as val') != -1
        assert res.index('even_longer_foo.other_value as other_val') != -1

    # print(res)

    def test_join_alias(self):
        q = '''
        from e:employees
        join s:salaries [emp_no]
        join d:departments [dept_no]
        select [dept_name, gender, salary_avg, salary_sd]'''
        res = prql.to_sql(q)
        print('\n\n\n\n' + res)
        assert res.index('JOIN salaries s ON e.emp_no = s.emp_no') != -1
        assert res.index('JOIN departments d ON e.dept_no = d.dept_no') != -1

    def test_join_type_any_side(self):
        q = 'from employees | join salaries [emp_no] side:left'
        res = prql.to_sql(q)
        print('\n\n\n\n' + res)
        assert res.index('LEFT JOIN') != -1
        q = 'from employees | join salaries side:left [emp_no]'
        res = prql.to_sql(q)
        print('\n\n\n\n' + res)
        assert res.index('LEFT JOIN') != -1

    def test_join_alias_with_where(self):
        q = '''
        from e:employees
        join s:salaries [emp_no]
        join d:departments [dept_no]
        filter e.salary > s.salary'''
        res = prql.to_sql(q)
        print('\n\n\n\n' + res)
        assert res.index('WHERE e.salary>s.salary') != -1

    def test_prql_employee_md(self):
        q = '''
        from employees
        join salaries [emp_no]
        aggregate by:[emp_no, gender] [
          emp_salary: average salary
        ]
        join de:dept_emp [emp_no] side:left
        aggregate by:[de.dept_no, gender] [
          salary_avg: average emp_salary,
          salary_sd: stddev emp_salary
        ]
        join departments [dept_no]
        select [dept_name, gender, salary_avg, salary_sd]'''
        res = prql.to_sql(q)
        # print(res)

        assert res.index('AVG(salary) as emp_salary') != -1
        assert res.index('GROUP BY emp_no,gender') != -1
        assert res.index('FROM `employees` employees_e') != -1
        assert res.index('JOIN salaries salaries_s ON employees_e.emp_no = salaries_s.emp_no') != -1
        assert res.index('JOIN departments departments_d ON employees_e.dept_no = departments_d.dept_no') != -1

    def test_prql_employee_md_with_join_alias(self):
        q = '''
        from salaries
        aggregate by:[emp_no] [
          emp_salary: average salary
        ]
        join t:titles [emp_no]
        join dept_emp side:left [emp_no]
        aggregate by:[dept_emp.dept_no, t.title] [
          avg_salary: average emp_salary
        ]
        join departments [dept_no]
        select [dept_name, title, avg_salary]'''
        res = prql.to_sql(q, True)

    # print(res)

    def test_prql_replace_tables_should_work_on_sort(self):
        q = '''
        from albums join tr:tracks [ AlbumId ]
        join ar:artists [ ArtistId ] 
        select [ albums.Title, tracks.Name , artists.Name ]  
        take 100 
        sort artists.Name order:desc'''
        res = prql.to_sql(q)
        print(res)
        # sort by has the new alias
        assert res.index('ORDER BY ar.Name') != -1
