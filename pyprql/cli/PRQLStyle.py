"""Pygments Style object for pyprql CLI."""
from pygments.style import Style
from pygments.token import (
    Comment,
    Error,
    Generic,
    Keyword,
    Name,
    Number,
    Operator,
    String,
    Token,
    Whitespace,
)


class PRQLStyle(Style):
    """Pygments version of the "native" vim theme.

    Inherits from pygments ``Style``,
    overriding values to create our colour scheme.
    The various style attributes are self-descriptive,
    and thoroughly documented on the pygments
    `website <https://pygments.org/docs/styledevelopment/>`_.
    """

    background_color = "#202020"
    highlight_color = "#404040"
    line_number_color = "#aaaaaa"
    background_color = "#202020"
    highlight_color = "#404040"
    line_number_color = "#aaaaaa"

    styles = {
        Token: "#d0d0d0",
        Whitespace: "#666666",
        Comment: "italic #999999",
        Comment.Preproc: "noitalic bold #cd2828",
        Comment.Special: "noitalic bold #e50808 bg:#520000",
        Keyword: "bold #6ab825",
        Keyword.Pseudo: "nobold",
        Operator.Word: "bold #6ab825",
        String: "#ed9d13",
        String.Other: "#ffa500",
        Number: "#3677a9",
        Name.Builtin: "#24909d",
        Name.Variable: "#40ffff",
        Name.Constant: "#40ffff",
        Name.Class: "underline #447fcf",
        Name.Function: "#447fcf",
        Name.Namespace: "underline #447fcf",
        Name.Exception: "#bbbbbb",
        Name.Tag: "bold #6ab825",
        Name.Attribute: "#bbbbbb",
        Name.Decorator: "#ffa500",
        Generic.Heading: "bold #ffffff",
        Generic.Subheading: "underline #ffffff",
        Generic.Deleted: "#d22323",
        Generic.Inserted: "#589819",
        Generic.Error: "#d22323",
        Generic.Emph: "italic",
        Generic.Strong: "bold",
        Generic.Prompt: "#aaaaaa",
        Generic.Output: "#cccccc",
        Generic.Traceback: "#d22323",
        Error: "bg:#e3d2d2 #a61717",
    }
