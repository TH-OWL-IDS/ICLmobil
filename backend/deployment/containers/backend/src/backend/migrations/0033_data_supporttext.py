from django.db import migrations



def add_data(apps, schema_editor):
    from django.db import connection
    with connection.cursor() as cursor:
        for cid, title_de, title_en, description_de, description_en in (
                (1, 'FAQ', 'FAQ', 'Häufig gestellte Fragen', 'Frequently asked questions'),
                (2, 'Troubleshooting', 'Troubleshooting', 'Was tun bei Problemen', 'What to do when problems come up'),
                (3, 'Notfall Hilfe', 'Emergency help', 'Hilfe in Notfällen', 'Help in case of emergencies'),
                (4, 'Spezielle Seiten', 'Special pages', 'Spezielle Seiten wie Rechtliches und Impressum', 'Special pages like Legal and Imprint'),
        ):
            cursor.execute("INSERT INTO backend_supporttextcategory (id, title, title_de, title_en, description, description_de, description_en) VALUES (%s, %s, %s, %s, %s, %s, %s) ON CONFLICT DO NOTHING;", [
                cid, title_de, title_de, title_en, description_de, description_de, description_en
            ])
        for eid, cid, sort_order, title_de, title_en, text_de, text_en, content_de, content_en in (
                (1, 1, 1, 'Test-Eintrag FAQ', 'Test entry FAQ', 'Test-Eintrag', 'Test entry', 'Test-<b>Eintrag</b>', 'Test <b>entry</b>'),
                (2, 2, 1, 'Test-Eintrag Troubleshooting', 'Test entry Troubleshooting', 'Test-Eintrag', 'Test entry', 'Test-<b>Eintrag</b>', 'Test <b>entry</b>'),
                (3, 3, 1, 'Test-Eintrag Notfall Hilfe', 'Test entry Emergency help', 'Test-Eintrag', 'Test entry', 'Test-<b>Eintrag</b>', 'Test <b>entry</b>'),
        ):
            cursor.execute("INSERT INTO backend_supporttextentry (id, category_id, sort_order, title, title_de, title_en, text, text_de, text_en, content, content_de, content_en, created_at, modified_at) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, now(), now()) ON CONFLICT DO NOTHING;", [
                eid, cid, sort_order, title_de, title_de, title_en, text_de, text_de, text_en, content_de, content_de, content_en
            ])


class Migration(migrations.Migration):
    dependencies = [
        ('backend', '0032_supporttextcategory_supporttextentry'),
    ]

    operations = [
        migrations.RunPython(add_data),
        migrations.RunSQL("""
            BEGIN;
            LOCK TABLE backend_supporttextcategory IN EXCLUSIVE MODE;
            SELECT setval('backend_supporttextcategory_id_seq',(SELECT GREATEST(1, MAX(id), nextval('backend_supporttextcategory_id_seq')-1) FROM backend_supporttextcategory));
            LOCK TABLE backend_supporttextentry IN EXCLUSIVE MODE;
            SELECT setval('backend_supporttextentry_id_seq',(SELECT GREATEST(1, MAX(id), nextval('backend_supporttextentry_id_seq')-1) FROM backend_supporttextentry));
            COMMIT;
            """),
    ]


