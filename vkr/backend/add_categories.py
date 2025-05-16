from lots.models import Category

categories_to_add = [
    "Живопись",
    "Скульптура",
    "Графика",
    "Фотография",
    "Декоративно-прикладное искусство",
    "Книги и рукописи",
    "Антиквариат",
    "Коллекционные предметы",
    "Ювелирные изделия",
    "Благотворительные лоты"
]

# Добавляем категории
for name in categories_to_add:
    category, created = Category.objects.get_or_create(name=name)
    if created:
        print(f"Добавлена категория: {name}")
    else:
        print(f"Категория уже существует: {name}")

print(f"Всего категорий: {Category.objects.count()}") 