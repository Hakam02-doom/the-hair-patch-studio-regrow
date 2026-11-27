/* The Hair Patch Studio – static-site helpers.
   1. Contact forms (MetForm) have no WordPress backend here: on submit, open a pre-filled email.
   2. WhatsApp chat button, as on thehairpatchstudio.com. */
(function () {
  var EMAIL = 'info@thehairpatchstudio.com';

  document.addEventListener('submit', function (e) {
    var form = e.target;
    if (!form || !form.closest || !form.closest('.mf-form-wrapper, .metform-form-content, form')) return;
    e.preventDefault();
    e.stopImmediatePropagation();
    var lines = [];
    var subject = 'Website enquiry';
    form.querySelectorAll('input, textarea, select').forEach(function (el) {
      if (!el.name || el.type === 'hidden' || el.type === 'submit' || el.type === 'checkbox') return;
      var label = (el.getAttribute('placeholder') || el.name).replace(/^mf-/, '');
      if (/subject/i.test(el.name) && el.value) subject = el.value;
      if (el.value) lines.push(label + ': ' + el.value);
    });
    window.location.href = 'mailto:' + EMAIL + '?subject=' + encodeURIComponent(subject) +
      '&body=' + encodeURIComponent(lines.join('\n'));
  }, true);

  var wa = document.createElement('a');
  wa.className = 'hps-whatsapp';
  wa.href = 'https://wa.me/447404902708';
  wa.target = '_blank';
  wa.rel = 'noopener';
  wa.setAttribute('aria-label', 'Chat with The Hair Patch Studio on WhatsApp');
  wa.innerHTML = '<svg viewBox="0 0 32 32" aria-hidden="true"><path d="M16 3C9 3 3.3 8.6 3.3 15.6c0 2.2.6 4.4 1.7 6.3L3 29l7.3-1.9c1.8 1 3.8 1.5 5.8 1.5 7 0 12.7-5.6 12.7-12.6S23 3 16 3zm0 23.1c-1.9 0-3.7-.5-5.3-1.5l-.4-.2-4.3 1.1 1.2-4.2-.3-.4a10.4 10.4 0 0 1-1.6-5.5C5.3 9.8 10.1 5.1 16 5.1s10.6 4.7 10.6 10.5S21.9 26.1 16 26.1zm5.8-7.8c-.3-.2-1.9-.9-2.2-1-.3-.1-.5-.2-.7.2-.2.3-.8 1-1 1.2-.2.2-.4.2-.7.1-.3-.2-1.3-.5-2.5-1.6-.9-.8-1.6-1.8-1.7-2.1-.2-.3 0-.5.1-.6l.5-.6c.2-.2.2-.3.3-.5.1-.2.1-.4 0-.6l-1-2.4c-.3-.6-.5-.5-.7-.5h-.6c-.2 0-.6.1-.9.4-.3.3-1.2 1.1-1.2 2.8s1.2 3.2 1.4 3.4c.2.2 2.4 3.6 5.7 5 .8.3 1.4.6 1.9.7.8.3 1.5.2 2.1.1.6-.1 1.9-.8 2.2-1.5.3-.7.3-1.4.2-1.5-.1-.2-.3-.3-.6-.4z"/></svg>';
  document.body.appendChild(wa);
})();
