from portal.models import Article


class AdminArticle(Article):
    class Meta:
        proxy = True
        verbose_name = "Статья"
        verbose_name_plural = "Статьи"
