from django.db import migrations

def add_data(apps, schema_editor):
    from django.conf import settings
    from filer.models import Folder, Image
    from backend.models import NewsType
    global data
    image_folder = Folder.objects.get(name='CMS')

    from django.db import connection

    with connection.cursor() as cursor:
        for category, entries in data.items():
            news_type = {
                'ICL_NEWS': NewsType.icl_news,
                'CAMPUS_NEWS': NewsType.campus_news,
            }[category]
            for entry in entries:
                image_name = entry['image'].split("/")[-1]
                image = Image.objects.get(name=image_name, folder=image_folder)
                cursor.execute(
                    "INSERT INTO backend_newsentry (news_type, header, header_de, header_en, sub_header, sub_header_de, sub_header_en, image_id, text, text_de, text_en, created_at, modified_at) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, now(), now()) ON CONFLICT DO NOTHING;",
                    [
                        news_type,
                        entry['header_de'],
                        entry['header_de'],
                        entry['header_en'],
                        entry['subHeader_de'],
                        entry['subHeader_de'],
                        entry['subHeader_en'],
                        image.id,
                        entry['text_de'],
                        entry['text_de'],
                        entry['text_en'],
                    ])



class Migration(migrations.Migration):
    dependencies = [
        ('backend', '0010_newsentry'),
    ]

    operations = [
        migrations.RunPython(add_data),
        migrations.RunSQL("""
        BEGIN;
        LOCK TABLE backend_newsentry IN EXCLUSIVE MODE;
        SELECT setval('backend_newsentry_id_seq',(SELECT GREATEST(MAX(id), nextval('backend_newsentry_id_seq')-1) FROM backend_newsentry));
        COMMIT;
        """),
    ]

data = {
    "ICL_NEWS": [
        {
            "id": 1,
            "title_de": "ICL Mobile",
            "title_en": "ICL Mobile",
            "image": "https://icl-mobile-data.s3.eu-central-1.amazonaws.com/placeholder/images/artwork1.png",
            "header_de": "Entdecke die Möglichkeiten",
            "header_en": "Discover the possibilities",
            "subHeader_de": "Was geht denn da?",
            "subHeader_en": "What's going on there?",
            "text_de": "Dies ist ein Beispieltext mit sinnlosen deutschen Wörtern. Einfach so stehen sie hier, ohne Bedeutung oder Zusammenhang, wie ein Wortsalat im Sommerregen. Es ist lustig, aber nicht sehr nützlich.",
            "text_en": "Lorem ipsum filler text, providing absolutely no meaning, purely to occupy space within this text field, making sure the word count aligns with the placeholder length. Just another meaningless English sentence or two thrown into the mix."
        }
    ],
    "CAMPUS_NEWS": [
        {
            "id": 1,
            "title_de": "Campus News",
            "title_en": "Campus News",
            "news_type": "icl_news",
            "image": "https://icl-mobile-data.s3.eu-central-1.amazonaws.com/placeholder/images/artwork1.png",
            "header_de": "Die neuen Scooter sind da!",
            "header_en": "The new scooters are here!",
            "subHeader_de": "Schon ausprobiert?",
            "subHeader_en": "Have you tried it yet?",
            "text_de": "Hier steht ein langer sinnfreier Fülltext mit ungefähr vierzig Wörtern. Dieser Text dient lediglich als Platzhalter und hat keinen weiteren Nutzen oder Zweck in diesem Kontext.",
            "text_en": "Another random English filler text to fill up space and give a sense of completeness. Just like a placeholder in design, these sentences have no real value but offer volume and consistency."
        },
        {
            "id": 2,
            "title_de": "Campus News",
            "title_en": "Campus News",
            "image": "https://icl-mobile-data.s3.eu-central-1.amazonaws.com/placeholder/images/artwork2.png",
            "header_de": "Spare mit der CO<sub>2</sub> Wallet",
            "header_en": "Save with the CO<sub>2</sub> Wallet",
            "subHeader_de": "Sparen ohne Ende!",
            "subHeader_en": "Save endlessly!",
            "text_de": "Dieser sinnfreie deutsche Fülltext soll etwa vierzig Wörter lang sein. Er füllt die Stelle des Textes aus, ohne dabei einen nennenswerten Inhalt zu liefern. So sieht es einfach besser aus.",
            "text_en": "Filling this section with purposeless text, we achieve balance and layout harmony. These English words stand here, random yet effective, ensuring a neat and polished presentation."
        },
        {
            "id": 3,
            "title_de": "Campus News",
            "title_en": "Campus News",
            "image": "https://icl-mobile-data.s3.eu-central-1.amazonaws.com/placeholder/images/artwork3.png",
            "header_de": "Neue Fußbälle",
            "header_en": "New footballs",
            "subHeader_de": "Kick it like Beckham!",
            "subHeader_en": "Kick it like Beckham!",
            "text_de": "Ein deutscher Fülltext, der keinerlei Bedeutung hat. Er enthält zufällige Worte, die zusammengestellt wurden, um eine ungefähre Wortanzahl von vierzig zu erreichen. Nur Platzhalter.",
            "text_en": "Placeholder text serves no real purpose but to showcase how content might appear. These English sentences add no value but maintain structure and visual appeal in this text field."
        },
        {
            "id": 4,
            "title_de": "Campus News",
            "title_en": "Campus News",
            "image": "https://icl-mobile-data.s3.eu-central-1.amazonaws.com/placeholder/images/artwork1.png",
            "header_de": "News #4",
            "header_en": "News #4",
            "subHeader_de": "Joghurt hat keine Gräten",
            "subHeader_en": "Yoghurt has no bones",
            "text_de": "In diesem deutschen Text finden sich ausschließlich sinnfreie Worte, die ohne tieferen Zusammenhang aneinandergereiht wurden. Ihr einziger Zweck ist das Auffüllen der vorgesehenen Zeichenanzahl.",
            "text_en": "This is filler text, placed here for illustrative purposes. It carries no intrinsic meaning and simply serves to fill space and complete the layout."
        }
    ]
}

