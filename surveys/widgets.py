from wtforms.widgets import html_params
from wtforms import SelectMultipleField, widgets


def select_multi_checkbox(field, ul_class='', **kwargs):
    # https://github.com/wtforms/wtforms/blob/60abf4fbb9fc5231f6525a2062e40fd88be240dc/docs/widgets.rst
    kwargs.setdefault('type', 'checkbox')
    field_id = kwargs.pop('id', field.id)

    kwargs.pop('class', None)

    html = ['<br/>']
    for value, label, checked in field.iter_choices():
        choice_id = u'%s-%s' % (field_id, value)
        options = dict(kwargs, name=field.name, value=value, id=choice_id)
        if checked:
            options['checked'] = 'checked'
        html.append(u'<label class="checkbox-inline" for="%s"><input %s>%s</label>' % (field_id, html_params(**options), label))
    html = u'\n'.join(html)
    return html


class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()

    def __init__(self, *args, **kwargs):
        super(MultiCheckboxField, self).__init__(*args, widget=select_multi_checkbox, **kwargs)
