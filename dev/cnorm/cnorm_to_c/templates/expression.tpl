{#- BEGIN expression::primary ---------------------------------- -#}

{%- macro index(subexpr) -%}
  [{{getattr(self, subexpr.expr.sub_type)(subexpr.expr)}}]
{%- endmacro -%}

{%- macro operator(subexpr) -%}
  {{subexpr.expr.op}}
{%- endmacro -%}

{%- macro call(subexpr) -%}
  ({{getattr(self, subexpr.expr.sub_type)(subexpr.expr)}})
{%- endmacro -%}

{%- macro parenthesis(expr) -%}
  ({{getattr(self, expr.body.sub_type)(expr.body)}})
{%- endmacro -%}

{#- END expression::primary ------------------------------------ -#}

{#- BEGIN expression::postfix ---------------------------------- -#}

{%- macro cast(expr) -%}
  ({{expr.type_name}}){{getattr(self, expr.subexpr.sub_type)(expr.subexpr)}}
{%- endmacro -%}

{%- macro sizeof(subexpr) -%}
  sizeof({{getattr(self, subexpr.expr.sub_type)(subexpr.expr)}})
{%- endmacro -%}

{%- macro struct(expr) -%}
  {{expr.expr.op}}{{expr.expr.struct_id}}
{%- endmacro -%}

{%- macro post(expr) -%}
  {%- if expr.has_key("postfix") -%}
    {%- for subexpr in expr.postfix -%}
      {{getattr(self, subexpr.sub_type)(subexpr)}}
    {%- endfor -%}
  {%- endif -%}
{%- endmacro -%}

{%- macro terminal(expr) -%}
  {# FIXME : useless?
  {%- if expr.has_key("cast") -%}
    {{expr.cast}}
  {%- endif -%}
  #}
  {%- if expr.operator == "id" -%}
    {{expr.primary_id}}
  {%- elif expr.operator == "primary" -%}
    {{expr.primary}}
  {%- endif -%}
  {{post(expr)}}
{%- endmacro -%}

{%- macro ternary(expr) -%}
    {{getattr(self, expr.condition.sub_type)(expr.condition)}}
    {{-" ? "}}
    {{- getattr(self, expr.then.sub_type)(expr.then)}}
    {{-" : "}}
    {{- getattr(self, expr.else.sub_type)(expr.else)}}
{%- endmacro -%}

{%- macro binary(expr) -%}
    {{getattr(self, expr.left.sub_type)(expr.left)}}{{" "}}
    {{-expr.op}}{{" "}}
    {{- getattr(self, expr.right.sub_type)(expr.right)}}
{%- endmacro -%}

{%- macro unary(expr) -%}
  {{expr.op}}{{getattr(self, expr.subexpr.sub_type)(expr.subexpr)}}
{%- endmacro -%}

{#- END expression::postfix ------------------------------------ -#}

{%- macro expression(expr) -%}
  {%- if expr.sub_type != 'expression' -%}
  {{getattr(self, expr.sub_type)(expr)}}
  {%- else -%}
  {{getattr(self, expr.sub_type)(expr.subexpr)}};
  {%- endif -%}
{%- endmacro -%}

{% block main %}
{% endblock %}
