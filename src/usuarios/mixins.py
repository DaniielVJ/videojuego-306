from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin


class PlayerRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    pass


class GmRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_gm
