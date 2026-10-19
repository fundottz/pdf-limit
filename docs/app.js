/* Аналитика и поведение тестового лендинга. YM_ID = 0 — счётчик не подключён. */
var YM_ID = 0;

function goal(name) {
  if (YM_ID && typeof window.ym === 'function') {
    window.ym(YM_ID, 'reachGoal', name);
  }
}

document.addEventListener('DOMContentLoaded', function () {
  // Тариф из адреса: ?t=690 — срочный, иначе стандартный 299
  var params = new URLSearchParams(window.location.search);
  var tariff = params.get('t') === '690' ? 690 : 299;
  var goalName = tariff === 690 ? 'pay_click_690' : 'pay_click';

  if (document.getElementById('price')) {
    document.getElementById('price').textContent = String(tariff);
    document.getElementById('sum-price').textContent = tariff + ' ₽';
    document.getElementById('sum-total').textContent = tariff + ' ₽';
    document.title = 'Оплата ' + tariff + ' ₽ — сжатие PDF под лимит';
    if (tariff === 690) {
      document.getElementById('tariff-lead').textContent = 'Срочно: большие файлы до 30 МБ, 100+ страниц, гарантия приёмки.';
      document.getElementById('sum-item').textContent = 'Сжатие одного PDF, срочно';
      document.getElementById('row-priority').hidden = false;
    }
  }

  // Клики по кнопкам оплаты — главная метрика теста
  document.querySelectorAll('[data-goal="pay_click"]').forEach(function (el) {
    el.addEventListener('click', function () {
      goal(goalName);
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

      goal(goalName);
      status.textContent = 'Оплата подключается. Мы напишем на ' + email.value + ', когда можно будет сжать файл.';
      status.classList.add('status--show');
      var btn = document.getElementById('pay-btn');
      btn.setAttribute('disabled', 'disabled');
      btn.textContent = 'Заявка принята';
    });
  }
});
