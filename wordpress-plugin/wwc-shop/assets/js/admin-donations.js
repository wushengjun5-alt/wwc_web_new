/* WWC Donations Admin JS */
(function ($) {
    'use strict';

    console.log('[WWC Donations] JS loaded. wwcDonations =', window.wwcDonations);

    var cfg   = window.wwcDonations || {};
    var ajax  = cfg.ajaxUrl || (typeof ajaxurl !== 'undefined' ? ajaxurl : '');
    var nonce = cfg.nonce  || '';
    var i18n  = cfg.i18n   || {};

    console.log('[WWC Donations] ajaxUrl =', ajax, '| nonce =', nonce ? '(set)' : '(EMPTY!)');

    // ── Utility ──────────────────────────────────────────────────

    function showNotice(msg, type) {
        var el = $('#wwc-don-notice');
        if (!el.length) {
            console.warn('[WWC Donations] #wwc-don-notice not found in DOM');
            return;
        }
        el.attr('class', 'notice notice-' + (type || 'success') + ' is-dismissible')
          .html('<p>' + $('<div>').text(msg).html() + '</p>')
          .show();
        $('html, body').animate({ scrollTop: el.offset().top - 60 }, 300);
    }

    function postAjax(action, data, cb) {
        data.action = action;
        data.nonce  = nonce;
        console.log('[WWC Donations] postAjax →', action, data);
        $.post(ajax, data)
            .done(function (res) {
                console.log('[WWC Donations] AJAX response for', action, ':', res);
                if (res && res.success) {
                    cb(null, res.data);
                } else {
                    var msg = (res && res.data && res.data.message) ? res.data.message : (i18n.error || 'Erreur');
                    cb(msg);
                }
            })
            .fail(function (xhr) {
                console.error('[WWC Donations] AJAX failed:', xhr.status, xhr.responseText);
                cb(i18n.error || 'Erreur réseau (' + xhr.status + ')');
            });
    }

    // ── Donations list — save status ──────────────────────────────

    $(document).on('click', '.don-save-btn', function (e) {
        e.preventDefault();
        console.log('[WWC Donations] .don-save-btn clicked');
        var btn    = $(this);
        var id     = btn.data('id');
        var status = $('#don-row-' + id).find('.don-status-select').val();
        console.log('[WWC Donations] donation id =', id, 'status =', status);
        btn.prop('disabled', true).text('…');

        postAjax('wwc_admin_update_donation', { id: id, status: status }, function (err) {
            btn.prop('disabled', false).text(err ? 'Enregistrer' : '✓ OK');
            showNotice(err || i18n.saveSuccess || 'Enregistré.', err ? 'error' : 'success');
        });
    });

    // ── Projects list — delete ────────────────────────────────────

    $(document).on('click', '.proj-delete-btn', function (e) {
        e.preventDefault();
        console.log('[WWC Donations] .proj-delete-btn clicked');
        if (!confirm(i18n.confirmDelete || 'Supprimer ?')) return;
        var btn      = $(this);
        var id       = btn.data('id');
        var redirect = btn.data('redirect') || '';
        btn.prop('disabled', true);

        postAjax('wwc_admin_delete_project', { id: id }, function (err) {
            if (err) {
                showNotice(err, 'error');
                btn.prop('disabled', false);
            } else {
                showNotice(i18n.deleteSuccess || 'Supprimé.', 'success');
                if (redirect) {
                    setTimeout(function () { window.location.href = redirect; }, 800);
                } else {
                    $('#proj-row-' + id).fadeOut(400, function () { $(this).remove(); });
                }
            }
        });
    });

    // ── Project form — save (create / update) ────────────────────

    $(document).on('submit', '#wwc-project-form', function (e) {
        e.preventDefault();
        e.stopPropagation();
        console.log('[WWC Donations] #wwc-project-form submit intercepted');
        var form = $(this);
        var id   = parseInt(form.data('id'), 10) || 0;
        var btn  = form.find('button[type=submit]');
        btn.prop('disabled', true).text('…');

        var data = {
            id:             id,
            title:          form.find('[name=title]').val(),
            title_en:       form.find('[name=title_en]').val(),
            description:    form.find('[name=description]').val(),
            description_en: form.find('[name=description_en]').val(),
            school:         form.find('[name=school]').val(),
            category:       form.find('[name=category]').val(),
            goal_amount:    form.find('[name=goal_amount]').val(),
            currency:       form.find('[name=currency]').val(),
            deadline:       form.find('[name=deadline]').val(),
            country_id:     form.find('[name=country_id]').val(),
            is_active:      form.find('[name=is_active]').is(':checked') ? 1 : 0,
            is_featured:    form.find('[name=is_featured]').is(':checked') ? 1 : 0,
        };
        console.log('[WWC Donations] project form data:', data);

        postAjax('wwc_admin_save_project', data, function (err, res) {
            btn.prop('disabled', false);
            if (err) {
                showNotice(err, 'error');
                btn.text(id ? 'Enregistrer' : 'Créer le projet');
            } else {
                var label = id ? 'Enregistré' : 'Créé';
                showNotice((res && res.message) || i18n.saveSuccess || label + '.', 'success');
                btn.text('✓ ' + label);
                if (!id && res && res.id) {
                    form.data('id', res.id);
                    if (history.replaceState) {
                        var url = new URL(window.location.href);
                        url.searchParams.set('action', 'edit');
                        url.searchParams.set('id', res.id);
                        history.replaceState({}, '', url.toString());
                    }
                }
            }
        });
    });

    // ── Countries — edit btn fills form ──────────────────────────

    $(document).on('click', '.country-edit-btn', function (e) {
        e.preventDefault();
        console.log('[WWC Donations] .country-edit-btn clicked');
        var btn = $(this);
        $('#country-id').val(btn.data('id'));
        $('#country-name').val(btn.data('name'));
        $('#country-name-en').val(btn.data('name_en'));
        $('#country-name-ar').val(btn.data('name_ar'));
        $('#country-slug').val(btn.data('slug'));
        $('#country-flag').val(btn.data('flag'));
        $('#country-active').prop('checked', String(btn.data('active')) === '1');
        $('#country-form-title').text('Modifier le pays');
        $('#country-form-reset').show();
        var target = $('#wwc-country-form');
        if (target.length) {
            $('html, body').animate({ scrollTop: target.offset().top - 60 }, 300);
        }
    });

    $(document).on('click', '#country-form-reset', function (e) {
        e.preventDefault();
        $('#wwc-country-form')[0].reset();
        $('#country-id').val(0);
        $('#country-form-title').text('Ajouter un pays');
        $(this).hide();
    });

    // ── Countries — save ─────────────────────────────────────────

    $(document).on('submit', '#wwc-country-form', function (e) {
        e.preventDefault();
        e.stopPropagation();
        console.log('[WWC Donations] #wwc-country-form submit intercepted');
        var form = $(this);
        var btn  = form.find('button[type=submit]');
        btn.prop('disabled', true).text('…');

        var data = {
            country_id: $('#country-id').val(),
            name:       $('#country-name').val(),
            name_en:    $('#country-name-en').val(),
            name_ar:    $('#country-name-ar').val(),
            slug:       $('#country-slug').val(),
            flag_emoji: $('#country-flag').val(),
            is_active:  $('#country-active').is(':checked') ? 1 : 0,
        };
        console.log('[WWC Donations] country form data:', data);

        postAjax('wwc_admin_save_country', data, function (err, res) {
            btn.prop('disabled', false).text('Enregistrer');
            if (err) {
                showNotice(err, 'error');
            } else {
                showNotice((res && res.message) || i18n.saveSuccess || 'Enregistré.', 'success');
                form[0].reset();
                $('#country-id').val(0);
                $('#country-form-title').text('Ajouter un pays');
                $('#country-form-reset').hide();
                setTimeout(function () { window.location.reload(); }, 1000);
            }
        });
    });

    // ── Countries — delete ────────────────────────────────────────

    $(document).on('click', '.country-delete-btn', function (e) {
        e.preventDefault();
        console.log('[WWC Donations] .country-delete-btn clicked');
        if (!confirm(i18n.confirmDelete || 'Supprimer ?')) return;
        var btn = $(this);
        var id  = btn.data('id');
        btn.prop('disabled', true);

        postAjax('wwc_admin_delete_country', { id: id }, function (err) {
            if (err) {
                showNotice(err, 'error');
                btn.prop('disabled', false);
            } else {
                showNotice(i18n.deleteSuccess || 'Supprimé.', 'success');
                $('#country-row-' + id).fadeOut(400, function () { $(this).remove(); });
            }
        });
    });

})(jQuery);
