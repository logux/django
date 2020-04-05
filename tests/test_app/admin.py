from django.contrib import admin

from tests.test_app.models import Cat


class CatAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'age',
    )
    search_fields = ('name',)


admin.site.register(Cat, CatAdmin)
