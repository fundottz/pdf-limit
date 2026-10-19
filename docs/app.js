/* Аналитика и поведение тестового лендинга. YM_ID = 0 — счётчик не подключён. */
var YM_ID = 0;

function goal(name) {
  if (YM_ID && typeof window.ym === 'function') {
    window.ym(YM_ID, 'reachGoal', name);
  }
}

document.addEventListener('DOMContentLoaded', function () {
  // Клики по кнопкам оплаты — главная метрика теста
  document.querySelectorAll('[data-goal="pay_click"]').forEach(function (el) {
    el.addEventListener('click', function () {
      goal('pay_click');
    });
  });

  var form = document.getElementById('pay-form');
  if (form) {
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var email = document.getElementById('email');
      var consent = document.getElementById('consent');
      var status = document.getElementById('status');

      if (!email.value || email.value.indexOf('@') === -1) {
        email.focus();
        return;
      }
      if (!consent.checked) {
        consent.focus();
        return;
      }

      goal('pay_click');
      status.textContent = 'Оплата подключается. Мы напишем на ' + email.value + ', когда можно будет сжать файл.';
      status.classList.add('status--show');
      var btn = document.getElementById('pay-btn');
      btn.setAttribute('disabled', 'disabled');
      btn.textContent = 'Заявка принята';
    });
  }
});
