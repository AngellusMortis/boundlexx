from django.conf import settings
from django.core.files.storage import FileSystemStorage
from storages.backends.azure_storage import AzureStorage


def select_storage(name):
    if "AzureStorage" in settings.DEFAULT_FILE_STORAGE:
        return AzureStorage(azure_container=f"{settings.AZURE_CONTAINER_PREFIX}{name}")
    return FileSystemStorage()
