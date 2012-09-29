{%- extends 'expression.tpl' -%}

{%- macro compound(stmt) -%}
{
  {%- for sub_stmt in stmt.stmts %}
  {{getattr(self, sub_stmt.sub_type)(sub_stmt)}}
  {%- endfor %}
}
{%- endmacro -%}

{%- macro expression_statement(stmt) -%}
  {{expression(stmt.subexpr)}};
{%- endmacro -%}

{%- macro keyword_condition(stmt, keyword) -%}
  {{keyword}} ({{expression(stmt.condition)}})
{%- endmacro -%}

{%- macro statement_base(stmt) -%}
  {{keyword_condition(stmt, stmt.keyword)}}
{{getattr(self, stmt.stmt.sub_type)(stmt.stmt)}}
{%- endmacro -%}

{%- macro for_expression(stmt, field) -%}
  {%- if stmt.has_key(field) -%}
  {{expression(stmt.__getitem__(field))}}
  {%- endif -%}
{%- endmacro -%}

{%- macro iteration(stmt) -%}
  {%- if stmt.keyword == 'while'-%}
    {{statement_base(stmt)}}
  {%- elif stmt.keyword == 'for' -%}
    for ({{for_expression(stmt, 'for_init')}};
	 {{-for_expression(stmt, 'condition')}};
	 {{-for_expression(stmt, 'for_each')}})
{{getattr(self, stmt.stmt.sub_type)(stmt.stmt)}}
  {%- else -%}
do
{{getattr(self, stmt.stmt.sub_type)(stmt.stmt)}}
{{keyword_condition(stmt, 'while')}};
  {%- endif -%}
{%- endmacro -%}

{%- macro labeled(stmt) -%}
{%- if stmt.has_key('keyword') -%}
{{stmt.keyword}}:
{%- else -%}
{{stmt.label}}:
{%- endif %}
{{getattr(self, stmt.stmt.sub_type)(stmt.stmt)}}
{%- endmacro -%}

{%- macro jump(stmt) -%}
  {%- if stmt.keyword == "return"-%}
  return{% if stmt.has_key('condition') %} ({{expression(stmt.condition)}}){% endif %}
  {%- else -%}
  {{stmt.keyword}}{% if stmt.keyword == "goto"%} {{stmt.label}}{% endif -%}
  {%- endif -%};
{%- endmacro -%}

{%- macro selection(stmt) -%}
  {{statement_base(stmt)}}
  {%- if stmt.has_key('else') %}
else
{{getattr(self, stmt.stmt.sub_type)(stmt.stmt)}}
  {%- endif -%}
{%- endmacro -%}

{%- macro statement(stmt) -%}
  {{getattr(self, stmt.sub_type)(stmt)}}
{%- endmacro -%}

{%- if tree.has_key('unittest') and tree.unittest == True-%}
{{statement(tree)}}
{%- endif -%}
