{% extends 'full.tpl'%}

{% block markdowncell scoped %}
<div class="cell border-box-sizing text_cell rendered">
{%- if resources.global_content_filter.include_input_prompt-%}
{{ self.empty_in_prompt() }}
{%- endif -%}
<div class="inner_cell">
{% set srclist = cell.source.split('\n') %}
{% set title = srclist[0] %}
{% if 'Prerequisites' in title %}

<div class="text_cell_render border-box-sizing rendered_html">
<div class="w3-panel w3-leftbar w3-border-green w3-pale-green w3-padding-small">
    <h3><i class="fa fa-star"></i>{{ title.lstrip('#') }}</h3>
    {{ srclist[1:] | join('\n') | markdown2html | strip_files_prefix }}
</div>
</div>

{% elif 'Overview' in title %}

<div class="text_cell_render border-box-sizing rendered_html">
<div class="w3-panel w3-leftbar w3-border-green w3-pale-green w3-padding-small">
    <h3><i class="fa fa-file-o"></i>{{ title.lstrip('#') }}</h3>
    {{ srclist[1:] | join('\n') | markdown2html | strip_files_prefix }}
</div>
</div>

{% elif 'Info' in title %}
{% set subtitle = title.split(':')[1:] %}

<div class="text_cell_render border-box-sizing rendered_html">
<div class="w3-panel w3-leftbar w3-border-blue w3-pale-blue w3-padding-small">
    <h3> <i class="fa fa-info-circle"></i>{{ ':'.join(subtitle) }}</h3>
    {{ srclist[1:] | join('\n') | markdown2html | strip_files_prefix }}
</div>
</div>

{% elif 'Exercise' in title %}
{% set subtitle = title.split(':')[1:] %}

<div class="text_cell_render border-box-sizing rendered_html">
<div class="w3-panel w3-leftbar w3-border-yellow w3-pale-yellow w3-padding-small">
    <h3> <i class="fa fa-pencil-square-o"></i>{{ ':'.join(subtitle) }}</h3>
    <div class="w3-text-black">
    {{ srclist[1:] | join('\n') | markdown2html | strip_files_prefix }}
    </div>
</div>
</div>

{% elif 'Solution' in title %}
{% set subtitle = title.split(':')[1:] %}

<div class="text_cell_render border-box-sizing rendered_html">
<div class="w3-panel w3-leftbar w3-border-blue w3-black w3-padding-small w3-hover-pale-blue">
    <h3> <i class="fa fa-eye"></i>{{ title.lstrip('#') }}</h3>
    {{ srclist[1:] | join('\n') | markdown2html | strip_files_prefix }}
</div>
</div>

{% elif 'Key Points' in title %}

<div class="text_cell_render border-box-sizing rendered_html">
<div class="w3-panel w3-leftbar w3-border-green w3-pale-green w3-padding-small">
    <h3> <i class="fa fa-key"></i></i>{{ title.lstrip('#') }}</h3>
    {{ srclist[1:] | join('\n') | markdown2html | strip_files_prefix }}
</div>
</div>

{% else %}

<div class="text_cell_render border-box-sizing rendered_html">
    {{ cell.source  | markdown2html | strip_files_prefix }}
</div>

{% endif %}
</div>
</div>
{%- endblock markdowncell %}
