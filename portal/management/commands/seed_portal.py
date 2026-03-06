from django.core.management.base import BaseCommand

from portal.models import Article, Brand, Category, Device, ErrorCode


class Command(BaseCommand):
    help = "Populate the portal with multilingual demo SEO content."

    def handle(self, *args, **options):
        Article.objects.all().delete()
        ErrorCode.objects.all().delete()
        Device.objects.all().delete()
        Brand.objects.all().delete()
        Category.objects.all().delete()

        self.create_categories()
        self.create_brands()
        self.create_devices()
        self.create_articles()
        self.create_error_codes()
        self.stdout.write(self.style.SUCCESS("Portal multilingual demo content created."))

    def seo_defaults(self, uk, ru, en):
        return {
            "seo_title": uk,
            "seo_title_ru": ru,
            "seo_title_en": en,
            "meta_description": uk[:255],
            "meta_description_ru": ru[:255],
            "meta_description_en": en[:255],
        }

    def create_categories(self):
        categories = [
            {
                "slug": "news",
                "position": 1,
                "name": ("Новини техніки", "Новости техники", "Tech News"),
                "description": (
                    "Останні новини про гаджети, побутову техніку та розумний дім.",
                    "Последние новости о гаджетах, бытовой технике и умном доме.",
                    "Latest updates on gadgets, appliances, and smart home devices.",
                ),
            },
            {
                "slug": "reviews",
                "position": 2,
                "name": ("Огляди пристроїв", "Обзоры устройств", "Device Reviews"),
                "description": (
                    "Практичні огляди техніки з фокусом на реальне використання.",
                    "Практические обзоры техники с фокусом на реальное использование.",
                    "Hands-on reviews focused on real-world usage and buying decisions.",
                ),
            },
            {
                "slug": "comparisons",
                "position": 3,
                "name": ("Порівняння техніки", "Сравнения техники", "Comparisons"),
                "description": (
                    "Порівняння моделей і брендів, які допомагають вибрати техніку.",
                    "Сравнения моделей и брендов, которые помогают выбрать технику.",
                    "Head-to-head comparisons that help readers choose the right device.",
                ),
            },
            {
                "slug": "guides",
                "position": 4,
                "name": ("Інструкції та поради", "Инструкции и советы", "Guides & Tips"),
                "description": (
                    "Догляд, обслуговування та корисні поради з використання техніки.",
                    "Уход, обслуживание и полезные советы по использованию техники.",
                    "Maintenance instructions and practical tips for everyday tech use.",
                ),
            },
            {
                "slug": "errors",
                "position": 5,
                "name": ("Коди помилок техніки", "Коды ошибок техники", "Error Codes"),
                "description": (
                    "Розшифрування кодів помилок з причинами та кроками виправлення.",
                    "Расшифровка кодов ошибок с причинами и шагами исправления.",
                    "Appliance error code explanations with causes and repair steps.",
                ),
            },
        ]
        for item in categories:
            Category.objects.create(
                slug=item["slug"],
                position=item["position"],
                name=item["name"][0],
                name_ru=item["name"][1],
                name_en=item["name"][2],
                description=item["description"][0],
                description_ru=item["description"][1],
                description_en=item["description"][2],
                **self.seo_defaults(*item["name"]),
            )

    def create_brands(self):
        brands = [
            {
                "slug": "apple",
                "name": ("Епл", "Эппл", "Apple"),
                "description": (
                    "Екосистема Apple, iPhone, MacBook і розумний дім.",
                    "Экосистема Apple, iPhone, MacBook и умный дом.",
                    "Apple ecosystem coverage including iPhone, MacBook, and smart home devices.",
                ),
                "website": "https://www.apple.com/",
            },
            {
                "slug": "samsung",
                "name": ("Самсунг", "Самсунг", "Samsung"),
                "description": (
                    "Смартфони, телевізори та побутова техніка Samsung.",
                    "Смартфоны, телевизоры и бытовая техника Samsung.",
                    "Samsung smartphones, TVs, and home appliances.",
                ),
                "website": "https://www.samsung.com/",
            },
            {
                "slug": "lg",
                "name": ("ЕлДжі", "ЛЖ", "LG"),
                "description": (
                    "Пральні машини, холодильники та телевізори LG.",
                    "Стиральные машины, холодильники и телевизоры LG.",
                    "LG appliances, TVs, washing machines, and refrigerators.",
                ),
                "website": "https://www.lg.com/",
            },
            {
                "slug": "bosch",
                "name": ("Бош", "Бош", "Bosch"),
                "description": (
                    "Побутова техніка Bosch та поради з обслуговування.",
                    "Бытовая техника Bosch и советы по обслуживанию.",
                    "Bosch household appliances and maintenance guidance.",
                ),
                "website": "https://www.bosch-home.com/",
            },
        ]
        for item in brands:
            Brand.objects.create(
                slug=item["slug"],
                name=item["name"][0],
                name_ru=item["name"][1],
                name_en=item["name"][2],
                description=item["description"][0],
                description_ru=item["description"][1],
                description_en=item["description"][2],
                website=item["website"],
                **self.seo_defaults(*item["name"]),
            )

    def create_devices(self):
        devices = [
            {
                "slug": "iphone-16-pro",
                "brand": "apple",
                "category": "reviews",
                "name": ("iPhone 16 Pro", "iPhone 16 Pro", "iPhone 16 Pro"),
                "device_type": ("Смартфон", "Смартфон", "Smartphone"),
                "description": (
                    "Флагман Apple для оглядів і порівнянь.",
                    "Флагман Apple для обзоров и сравнений.",
                    "Apple flagship smartphone used in review and comparison coverage.",
                ),
            },
            {
                "slug": "galaxy-s26-ultra",
                "brand": "samsung",
                "category": "comparisons",
                "name": ("Galaxy S26 Ultra", "Galaxy S26 Ultra", "Galaxy S26 Ultra"),
                "device_type": ("Смартфон", "Смартфон", "Smartphone"),
                "description": (
                    "Флагманський смартфон Samsung для порівнянь.",
                    "Флагманский смартфон Samsung для сравнений.",
                    "Samsung flagship phone featured in comparison articles.",
                ),
            },
            {
                "slug": "lg-washpro-500",
                "brand": "lg",
                "category": "guides",
                "name": ("LG WashPro 500", "LG WashPro 500", "LG WashPro 500"),
                "device_type": ("Пральна машина", "Стиральная машина", "Washing machine"),
                "description": (
                    "Демо-модель для гайдів і кодів помилок.",
                    "Демо-модель для гайдов и кодов ошибок.",
                    "Demo washer used in guides and error code content.",
                ),
            },
        ]
        for item in devices:
            Device.objects.create(
                slug=item["slug"],
                brand=Brand.objects.get(slug=item["brand"]),
                category=Category.objects.get(slug=item["category"]),
                name=item["name"][0],
                name_ru=item["name"][1],
                name_en=item["name"][2],
                device_type=item["device_type"][0],
                device_type_ru=item["device_type"][1],
                device_type_en=item["device_type"][2],
                description=item["description"][0],
                description_ru=item["description"][1],
                description_en=item["description"][2],
                **self.seo_defaults(*item["name"]),
            )

    def create_articles(self):
        articles = [
            {
                "slug": "smart-home-trends-2026",
                "category": "news",
                "brand": "samsung",
                "title": (
                    "Тренди розумного дому, які визначать 2026 рік",
                    "Тренды умного дома, которые определят 2026 год",
                    "Smart Home Trends That Will Define 2026",
                ),
                "excerpt": (
                    "ШІ в побутовій техніці та енергоефективність стають базою нового покоління пристроїв.",
                    "ИИ в бытовой технике и энергоэффективность становятся базой нового поколения устройств.",
                    "AI-powered appliances and energy efficiency are shaping the next generation of smart homes.",
                ),
                "content": (
                    "Виробники переходять від голосових команд до прогнозованої автоматизації. Нові пристрої аналізують звички користувача й підказують обслуговування.\n\nУ 2026 році найціннішими будуть не декоративні екрани, а корисні сценарії економії ресурсів.\n\nТакі новини добре працюють як вхідна точка для переходу в огляди, порівняння та інструкції.",
                    "Производители переходят от голосовых команд к прогнозируемой автоматизации. Новые устройства анализируют привычки пользователя и подсказывают обслуживание.\n\nВ 2026 году наибольшую ценность дают не декоративные экраны, а полезные сценарии экономии ресурсов.\n\nТакие новости хорошо работают как входная точка для перехода в обзоры, сравнения и инструкции.",
                    "Manufacturers are moving from voice commands to predictive automation. New devices learn usage habits and surface maintenance hints.\n\nIn 2026, the most valuable upgrades are practical energy-saving workflows rather than decorative screens.\n\nThis type of news is an effective SEO entry point into reviews, comparisons, and guides.",
                ),
                "image": "https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&w=1200&q=80",
                "featured": True,
            },
            {
                "slug": "best-washing-machines-2026",
                "category": "reviews",
                "brand": "lg",
                "device": "lg-washpro-500",
                "title": (
                    "Найкращі пральні машини 2026 року",
                    "Лучшие стиральные машины 2026 года",
                    "Best Washing Machines 2026",
                ),
                "excerpt": (
                    "Добірка пральних машин із фокусом на ефективність, шум і надійність.",
                    "Подборка стиральных машин с фокусом на эффективность, шум и надежность.",
                    "A shortlist of washing machines that balance efficiency, noise, and reliability.",
                ),
                "content": (
                    "Сильні моделі 2026 року тихіші, простіші в обслуговуванні та краще визначають дисбаланс.\n\nПокупці дедалі частіше дивляться на вартість володіння, а не лише на місткість.\n\nУ цьому огляді пріоритетом є стабільність, прогнозована підтримка та ясна діагностика.",
                    "Сильные модели 2026 года тише, проще в обслуживании и лучше определяют дисбаланс.\n\nПокупатели все чаще смотрят на стоимость владения, а не только на вместимость.\n\nВ этом обзоре приоритетом являются стабильность, предсказуемая поддержка и понятная диагностика.",
                    "The strongest 2026 machines are quieter, easier to maintain, and better at detecting uneven loads.\n\nBuyers increasingly care about lifetime ownership cost rather than capacity alone.\n\nThis review prioritizes stability, predictable maintenance, and clear diagnostics.",
                ),
                "image": "https://images.unsplash.com/photo-1626806787461-102c1bfaaea1?auto=format&fit=crop&w=1200&q=80",
                "featured": True,
            },
            {
                "slug": "iphone-vs-samsung",
                "category": "comparisons",
                "brand": "apple",
                "device": "iphone-16-pro",
                "title": (
                    "iPhone 16 Pro vs Samsung Galaxy S26 Ultra",
                    "iPhone 16 Pro vs Samsung Galaxy S26 Ultra",
                    "iPhone 16 Pro vs Samsung Galaxy S26 Ultra",
                ),
                "excerpt": (
                    "Порівнюємо камери, батарею, ШІ-функції та щоденний досвід використання.",
                    "Сравниваем камеры, батарею, ИИ-функции и ежедневный опыт использования.",
                    "Comparing cameras, battery behavior, AI features, and daily experience.",
                ),
                "content": (
                    "Apple і Samsung змагаються вже не лише цифрами, а загальною якістю сценаріїв використання.\n\niPhone сильніший у довгій оптимізації, тоді як Galaxy пропонує більше гнучкості в апаратній частині.\n\nВибір залежить від екосистеми та реального щоденного робочого процесу.",
                    "Apple и Samsung конкурируют уже не только цифрами, а качеством ежедневных сценариев использования.\n\niPhone сильнее в долгосрочной оптимизации, тогда как Galaxy дает больше аппаратной гибкости.\n\nВыбор зависит от экосистемы и реального ежедневного рабочего процесса.",
                    "Apple and Samsung now compete on workflow polish rather than raw specs alone.\n\nThe iPhone wins on long-term optimization while the Galaxy offers broader hardware flexibility.\n\nThe right choice depends on ecosystem preference and real daily workflow.",
                ),
                "image": "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?auto=format&fit=crop&w=1200&q=80",
                "featured": True,
            },
            {
                "slug": "how-to-clean-washing-machine",
                "category": "guides",
                "brand": "lg",
                "device": "lg-washpro-500",
                "title": (
                    "Як почистити пральну машину без шкоди для барабана",
                    "Как почистить стиральную машину без вреда для барабана",
                    "How to Clean a Washing Machine",
                ),
                "excerpt": (
                    "Покрокова інструкція для видалення запаху, нальоту та засмічень.",
                    "Пошаговая инструкция по удалению запаха, налета и засоров.",
                    "A practical maintenance guide for removing odors, residue, and drain buildup.",
                ),
                "content": (
                    "Пральну машину варто чистити регулярно, а не лише після появи запаху.\n\nПочніть із лотка для мийного засобу, манжети люка та фільтра помпи.\n\nРегулярний догляд зменшує ризик появи кодів помилок і продовжує ресурс техніки.",
                    "Стиральную машину стоит чистить регулярно, а не только после появления запаха.\n\nНачните с лотка для моющего средства, манжеты люка и фильтра помпы.\n\nРегулярный уход снижает риск кодов ошибок и продлевает ресурс техники.",
                    "A washing machine should be cleaned on a schedule, not only after odors appear.\n\nStart with the detergent drawer, door seal, and pump filter.\n\nRoutine care reduces the chance of error codes and extends machine lifespan.",
                ),
                "image": "https://images.unsplash.com/photo-1581578731548-c64695cc6952?auto=format&fit=crop&w=1200&q=80",
                "featured": False,
            },
            {
                "slug": "remote-work-laptops-2026",
                "category": "news",
                "brand": "apple",
                "title": (
                    "Найкращі ноутбуки для віддаленої роботи у 2026 році",
                    "Лучшие ноутбуки для удаленной работы в 2026 году",
                    "Best Laptops for Remote Work in 2026",
                ),
                "excerpt": (
                    "Розбираємо моделі для дзвінків, браузера, документів і монтажу.",
                    "Разбираем модели для звонков, браузера, документов и монтажа.",
                    "A practical look at laptops for calls, browser-heavy work, documents, and light editing.",
                ),
                "content": (
                    "У 2026 році від робочого ноутбука чекають тиші, хорошої камери та повного дня автономності.\n\nВажлива не тільки потужність, а й передбачуваність у Zoom, браузері та офісних інструментах.\n\nТакі матеріали збирають і комерційний, і інформаційний трафік.",
                    "В 2026 году от рабочего ноутбука ждут тишины, хорошей камеры и полного дня автономности.\n\nВажна не только мощность, но и предсказуемость в Zoom, браузере и офисных инструментах.\n\nТакие материалы собирают и коммерческий, и информационный трафик.",
                    "In 2026, a work laptop is expected to be quiet, camera-ready, and reliable through a full day on battery.\n\nRaw performance matters less than predictability in Zoom, browsers, and office tools.\n\nThis topic captures both commercial and informational search intent.",
                ),
                "image": "https://images.unsplash.com/photo-1496181133206-80ce9b88a853?auto=format&fit=crop&w=1200&q=80",
                "featured": False,
            },
            {
                "slug": "dyson-v15-detect-review",
                "category": "reviews",
                "brand": "bosch",
                "title": (
                    "Огляд Dyson V15 Detect: чи варто переплачувати",
                    "Обзор Dyson V15 Detect: стоит ли переплачивать",
                    "Dyson V15 Detect Review",
                ),
                "excerpt": (
                    "Оцінюємо потужність, шум, ергономіку та реальну користь преміальних функцій.",
                    "Оцениваем мощность, шум, эргономику и реальную пользу премиальных функций.",
                    "A review of suction power, noise, ergonomics, and whether premium features pay off.",
                ),
                "content": (
                    "Цей пилосос часто хвалять за тягу та насадки, але висока ціна вимагає жорсткішої оцінки.\n\nУ побуті виграє якість прибирання шерсті й дрібного пилу.\n\nПреміальність має сенс лише тоді, коли реально економить час.",
                    "Этот пылесос часто хвалят за тягу и насадки, но высокая цена требует более строгой оценки.\n\nВ быту выигрывает качество уборки шерсти и мелкой пыли.\n\nПремиальность имеет смысл только тогда, когда реально экономит время.",
                    "This vacuum is often praised for suction and attachments, but its premium price deserves stricter scrutiny.\n\nIn daily use, it stands out on pet hair and fine dust pickup.\n\nPremium positioning only makes sense when it genuinely saves time.",
                ),
                "image": "https://images.unsplash.com/photo-1558317374-067fb5f30001?auto=format&fit=crop&w=1200&q=80",
                "featured": False,
            },
            {
                "slug": "macbook-air-vs-zenbook-14",
                "category": "comparisons",
                "brand": "apple",
                "title": (
                    "MacBook Air vs Zenbook 14: що краще для роботи і навчання",
                    "MacBook Air vs Zenbook 14: что лучше для работы и учебы",
                    "MacBook Air vs Zenbook 14",
                ),
                "excerpt": (
                    "Автономність, дисплей, порти та сумісність у реальних сценаріях.",
                    "Автономность, дисплей, порты и совместимость в реальных сценариях.",
                    "Battery life, display, ports, and software compatibility in real workflows.",
                ),
                "content": (
                    "MacBook Air виграє автономністю та тишею, а Zenbook сильніший у портах і гнучкості.\n\nЯкщо ви повністю в екосистемі Apple, вибір простіший.\n\nДля змішаних сценаріїв Windows-модель часто практичніша.",
                    "MacBook Air выигрывает автономностью и тишиной, а Zenbook сильнее по портам и гибкости.\n\nЕсли вы полностью в экосистеме Apple, выбор проще.\n\nДля смешанных сценариев Windows-модель часто практичнее.",
                    "The MacBook Air wins on battery life and silence, while the Zenbook is stronger on ports and flexibility.\n\nIf you live inside Apple’s ecosystem, the choice is simpler.\n\nFor mixed workflows, the Windows machine is often more practical.",
                ),
                "image": "https://images.unsplash.com/photo-1517336714739-489689fd1ca8?auto=format&fit=crop&w=1200&q=80",
                "featured": False,
            },
            {
                "slug": "how-to-choose-robot-vacuum",
                "category": "guides",
                "brand": "bosch",
                "title": (
                    "Як вибрати робот-пилосос без переплати",
                    "Как выбрать робот-пылесос без переплаты",
                    "How to Choose a Robot Vacuum Without Overpaying",
                ),
                "excerpt": (
                    "На що дивитися: навігація, висота корпуса, щітки та обслуговування.",
                    "На что смотреть: навигация, высота корпуса, щетки и обслуживание.",
                    "What matters most: navigation, body height, brushes, and maintenance effort.",
                ),
                "content": (
                    "Робот-пилосос варто оцінювати за стабільністю навігації, а не маркетинговими режимами.\n\nДля квартири важливі висота корпуса, пороги та простота очищення контейнера.\n\nНайкраща покупка не завжди найдорожча, а та, що вимагає мінімум ручного втручання.",
                    "Робот-пылесос стоит оценивать по стабильности навигации, а не по маркетинговым режимам.\n\nДля квартиры важны высота корпуса, пороги и простота очистки контейнера.\n\nЛучшая покупка не всегда самая дорогая, а та, что требует минимум ручного вмешательства.",
                    "A robot vacuum should be judged by navigation stability rather than marketing modes.\n\nFor apartments, body height, threshold handling, and bin cleaning matter most.\n\nThe best purchase is often not the most expensive one, but the one that needs the least manual intervention.",
                ),
                "image": "https://images.unsplash.com/photo-1585771724684-38269d6639fd?auto=format&fit=crop&w=1200&q=80",
                "featured": False,
            },
            {
                "slug": "smart-fridges-2026",
                "category": "news",
                "brand": "samsung",
                "title": (
                    "Розумні холодильники 2026: що реально змінилося",
                    "Умные холодильники 2026: что реально изменилось",
                    "Smart Fridges 2026: What Actually Changed",
                ),
                "excerpt": (
                    "Нові моделі стають енергоефективнішими та кориснішими в автоматизації дому.",
                    "Новые модели становятся энергоэффективнее и полезнее в автоматизации дома.",
                    "New models are becoming more energy efficient and more useful in smart-home automation.",
                ),
                "content": (
                    "Сегмент розумних холодильників переходить від демонстраційних функцій до практичної користі.\n\nПокращуються сповіщення про температуру, контроль витрат енергії та сервісні нагадування.\n\nДля SEO це сильний новинний кластер із переходом в огляди та порівняння.",
                    "Сегмент умных холодильников переходит от демонстрационных функций к практической пользе.\n\nУлучшаются уведомления о температуре, контроль расхода энергии и сервисные напоминания.\n\nДля SEO это сильный новостной кластер с переходом в обзоры и сравнения.",
                    "Smart fridges are moving from showcase features to practical value.\n\nTemperature alerts, energy tracking, and service reminders are improving noticeably.\n\nFor SEO, this is a strong news cluster that naturally links into reviews and comparisons.",
                ),
                "image": "https://images.unsplash.com/photo-1584568694244-14fbdf83bd30?auto=format&fit=crop&w=1200&q=80",
                "featured": True,
            },
            {
                "slug": "samsung-bespoke-ai-jet-ultra-review",
                "category": "reviews",
                "brand": "samsung",
                "title": (
                    "Огляд Samsung Bespoke AI Jet Ultra",
                    "Обзор Samsung Bespoke AI Jet Ultra",
                    "Samsung Bespoke AI Jet Ultra Review",
                ),
                "excerpt": (
                    "Оцінюємо потужність, шум, станцію очищення та зручність у квартирі.",
                    "Оцениваем мощность, шум, станцию очистки и удобство в квартире.",
                    "Reviewing power, noise, cleaning station quality, and everyday apartment usability.",
                ),
                "content": (
                    "Модель орієнтована на швидке прибирання без контакту з пилом після кожного циклу.\n\nГоловна перевага не в дизайні, а в поєднанні потужності та зручності станції очищення.\n\nТакий пилосос має сенс лише якщо реально спрощує регулярне прибирання.",
                    "Модель ориентирована на быструю уборку без контакта с пылью после каждого цикла.\n\nГлавное преимущество не в дизайне, а в сочетании мощности и удобства станции очистки.\n\nТакой пылесос имеет смысл только если реально упрощает регулярную уборку.",
                    "This model targets quick cleaning without dust contact after each cycle.\n\nIts real advantage is not design, but the combination of power and a convenient cleaning station.\n\nA premium vacuum only makes sense if it truly simplifies routine cleaning.",
                ),
                "image": "https://images.unsplash.com/photo-1558317374-067fb5f30001?auto=format&fit=crop&w=1200&q=80",
                "featured": False,
            },
        ]
        for item in articles:
            Article.objects.create(
                slug=item["slug"],
                category=Category.objects.get(slug=item["category"]),
                brand=Brand.objects.get(slug=item["brand"]),
                device=Device.objects.filter(slug=item.get("device")).first(),
                title=item["title"][0],
                title_ru=item["title"][1],
                title_en=item["title"][2],
                excerpt=item["excerpt"][0],
                excerpt_ru=item["excerpt"][1],
                excerpt_en=item["excerpt"][2],
                content=item["content"][0],
                content_ru=item["content"][1],
                content_en=item["content"][2],
                image=item["image"],
                featured=item["featured"],
                is_published=True,
                **self.seo_defaults(*item["title"]),
            )

    def create_error_codes(self):
        error_codes = [
            {
                "slug": "lg-oe-error",
                "brand": "lg",
                "device": "lg-washpro-500",
                "code": "OE",
                "title": (
                    "Помилка LG OE: машина не зливає воду",
                    "Ошибка LG OE: машина не сливает воду",
                    "LG OE Error: Why Your Washer Will Not Drain",
                ),
                "description": (
                    "Код OE вказує на проблему зі зливом води.",
                    "Код OE указывает на проблему со сливом воды.",
                    "The OE code points to a drainage problem.",
                ),
                "causes": (
                    "Засмічений фільтр помпи.\n\nПеретиснутий шланг.",
                    "Засорен фильтр помпы.\n\nПережат шланг.",
                    "Clogged pump filter.\n\nBent drain hose.",
                ),
                "solutions": (
                    "Вимкніть машину, почистьте фільтр і перевірте шланг.",
                    "Выключите машину, очистите фильтр и проверьте шланг.",
                    "Turn off the washer, clean the filter, and inspect the hose.",
                ),
            },
            {
                "slug": "samsung-4e-error",
                "brand": "samsung",
                "code": "4E",
                "title": (
                    "Помилка Samsung 4E: проблема з подачею води",
                    "Ошибка Samsung 4E: проблема с подачей воды",
                    "Samsung 4E Error: Water Supply Problem",
                ),
                "description": (
                    "Машина не може набрати воду за потрібний час.",
                    "Машина не может набрать воду за нужное время.",
                    "The appliance cannot take in water fast enough.",
                ),
                "causes": (
                    "Закритий кран.\n\nЗабруднений фільтр подачі.",
                    "Закрытый кран.\n\nЗагрязнен фильтр подачи.",
                    "Closed tap.\n\nDirty inlet filter.",
                ),
                "solutions": (
                    "Відкрийте кран і очистьте вхідний фільтр.",
                    "Откройте кран и очистите входной фильтр.",
                    "Open the tap and clean the inlet filter.",
                ),
            },
        ]
        for item in error_codes:
            ErrorCode.objects.create(
                slug=item["slug"],
                brand=Brand.objects.get(slug=item["brand"]),
                device=Device.objects.filter(slug=item.get("device")).first(),
                code=item["code"],
                title=item["title"][0],
                title_ru=item["title"][1],
                title_en=item["title"][2],
                description=item["description"][0],
                description_ru=item["description"][1],
                description_en=item["description"][2],
                causes=item["causes"][0],
                causes_ru=item["causes"][1],
                causes_en=item["causes"][2],
                solutions=item["solutions"][0],
                solutions_ru=item["solutions"][1],
                solutions_en=item["solutions"][2],
                **self.seo_defaults(*item["title"]),
            )
