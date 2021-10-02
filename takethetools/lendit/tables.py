import django_tables2 as tables
from .models import Tool, Note, Lendlog
from django.utils.html import format_html

ATTRS = {"class": "table table-responsive table-striped table-hover"}


class LenditTable(tables.Table):
    class Meta:
        attrs = ATTRS


class LendLogTable(tables.Table):

    image = tables.TemplateColumn(
        '<img src="/media/{{record.tool.img}}" style="width:60px;"> '
    )
    my_column = tables.TemplateColumn(
        verbose_name="Status",
        template_name="lendlog_table_button.html",
        orderable=False,
    )  # orderable not sortable

    class Meta:
        model = Lendlog
        attrs = ATTRS
        fields = ("tool", "from_date", "expected_end_date", "end_date", "lend_by")
        sequence = (
            "image",
            "tool",
            "from_date",
            "expected_end_date",
            "end_date",
            "lend_by",
        )


class ToolTable(tables.Table):

    image = tables.TemplateColumn(
        '<img src="/media/{{record.img}}" style="width:60px;"> '
    )
    my_column = tables.TemplateColumn(
        verbose_name="Auswählen",
        template_name="tool_table_button.html",
        orderable=False,
    )  # orderable not sortable

    class Meta:
        model = Tool
        attrs = ATTRS
        fields = (
            "name",
            "brand",
            "model",
            "owner",
            "description",
        )
        sequence = (
            "image",
            "name",
            "brand",
            "model",
            "owner",
            "description",
            "my_column",
        )

    def render_name(self, record):
        return format_html("<b>{}</b>", record.name)


class UserTable(LenditTable):
    # We cannot use the definition via Meta here,
    # as the Usermodel cannot be imported, but needs
    # to be fetched with get_user_model()
    username = tables.Column()
    email = tables.Column()


class NoteTable(tables.Table):
    class Meta:
        model = Note
        attrs = ATTRS
        fields = (
            "title",
            "author",
            "text",
            "prio",
        )
