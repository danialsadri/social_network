def make_activation(modeladmin, request, queryset):
    result = queryset.update(active=True)
    modeladmin.message_user(request, f"{result} Posts ware accepted")


make_activation.short_description = "تایید پست"


def make_deactivation(modeladmin, request, queryset):
    result = queryset.update(active=False)
    modeladmin.message_user(request, f"{result} Posts ware rejected")


make_deactivation.short_description = "رد پست"
