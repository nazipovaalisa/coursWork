from django.contrib import admin
from django import forms
from django.core.exceptions import ValidationError
from django.utils.safestring import mark_safe

from .models import *

class GenresInLine(admin.TabularInline):

    model = Film.genre.through

@admin.register(Film)
class FilmAdmin(admin.ModelAdmin):

    actions = ["publish", "unpublish"]

    inlines = [GenresInLine]
    exclude = ('genre',)
    list_display = ('name', 'is_posted')
    list_editable = ('is_posted',)
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ('show_image',)

    def show_image(self, obj):
        return mark_safe(f'<img src={obj.image.url} width="60" height="90">')

    def unpublish(self, request, queryset):
        row_update = queryset.update(is_posted=False)

    def publish(self, request, queryset):
        row_update = queryset.update(is_posted=True)

    show_image.short_description = "Изображение"

    publish.short_description ="Опубликовать"
    publish.allowed_permissions = ('change',)

    unpublish.short_description ="Снять с публикации"
    unpublish.allowed_permissions = ('change',)

class SeansForm(forms.ModelForm):

    class Meta:
        model = Seans
        exclude = ['slug']

    def clean(self): #проверка на доступность зала в данную дату и время
        all_seans = Seans.objects.filter(date_seans = self.cleaned_data['date_seans'], hall = self.cleaned_data['hall'])
        for seans in all_seans.all():
            if self.cleaned_data['time_seans'] == seans.time_seans:
                raise ValidationError('Зал в это время уже занят!')
        return self.cleaned_data

@admin.register(Seans)
class SeansAdmin(admin.ModelAdmin):

    form = SeansForm
    list_filter = ('date_seans',)

class TicketAdmin(admin.ModelAdmin):

    list_display = ('seans', 'row',  'seat', 'reserved', 'bought')
    list_filter = ('bought', 'reserved', 'seans')
    list_editable = ('bought', 'reserved',)

admin.site.register(Ticket, TicketAdmin)
admin.site.register(Genre)
admin.site.register(Hall)
admin.site.register(Bron)
admin.site.register(Cart)
admin.site.register(Customer)
