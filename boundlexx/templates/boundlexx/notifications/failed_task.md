A celery task failed!

Task Name: `{{ task.task_name }}`
Task Result: {{ base_url }}{% url 'admin:django_celery_results_taskresult_change' task.id %}

Output:{% for message in messages %}
```{% for line in message %}
{{ line }}{% endfor %}
```{% if not forloop.last %}%SPLIT_MESSAGE%{% endif %}
{% endfor %}
