"use strict";
var app_plugins = {
    checkbox_radio: function() {
        ($(".app-checkbox").length > 0 || $(".app-radio").length > 0) && $(".app-checkbox label, .app-radio label").each(function() { $(this).append("<span></span>") })
    },
    switch_button: function() { $(".switch").length > 0 && $(".switch").each(function() { $(this).append("<span></span>") }) },
    isotope: function() {
        if (0 === $(".grid").length) return !1;
        var t = $(".grid").isotope({ itemSelector: ".grid-element", layoutMode: "fitRows", percentPosition: !0 });
        $("button[data-filter]").on("click", function() {
            var e = $(this).attr("data-filter");
            t.isotope({ filter: e }), $(this).parents(".btn-group").find(".btn-primary").removeClass("btn-primary").addClass("btn-default"), $(this).removeClass("btn-default").addClass("btn-primary")
        }), $(window).resize(function() { setTimeout(function() { t.isotope("layout"), app.accordionFullHeightResize(), app.features.gallery.controlHeight(), app.spy() }, 100) })
    },
    formSpinner: function() {
        $("input.spinner").length > 0 && ($("input.spinner").each(function() { $(this).wrap('<div class="spinner-wrapper"></div>'), $(this).after('<button class="spinner-button-up"><span class="fa fa-angle-up"></span></button>'), $(this).after('<button class="spinner-button-down"><span class="fa fa-angle-down"></span></button>') }), $(".spinner-button-up").on("click", function() {
            var t = $(this).parent(".spinner-wrapper").find("input"),
                e = !!t.attr("data-spinner-max") && parseFloat(t.data("spinner-max")),
                a = !!t.attr("data-spinner-min") && parseFloat(t.data("spinner-min")),
                n = t.attr("data-spinner-step") ? parseFloat(t.data("spinner-step")) : 1,
                i = parseFloat(t.val()) + n;
            return !(void 0 !== e && !1 !== e && i > e) && (!(void 0 !== a && !1 !== a && i < a) && (t.val(i), !1))
        }), $(".spinner-button-down").on("click", function() {
            var t = $(this).parent(".spinner-wrapper").find("input"),
                e = !!t.attr("data-spinner-max") && parseFloat(t.data("spinner-max")),
                a = !!t.attr("data-spinner-min") && parseFloat(t.data("spinner-min")),
                n = t.attr("data-spinner-step") ? parseFloat(t.data("spinner-step")) : 1,
                i = parseFloat(t.val()) - n;
            return !(void 0 !== e && !1 !== e && i > e) && (!(void 0 !== a && !1 !== a && i < a) && (t.val(i), !1))
        }))
    },
    customScrollBar: function() { $(".scroll").length > 0 && $(".scroll").mCustomScrollbar({ axis: "y", autoHideScrollbar: !0, scrollInertia: 200, advanced: { autoScrollOnFocus: !1 } }) },
    bootstrap_select: function() { $(".bs-select").length > 0 && $(".bs-select").selectpicker({ iconBase: "", tickIcon: "fa fa-check" }) },
    select2: function() { $(".s2-select").length > 0 && $(".s2-select").select2({ minimumResultsForSearch: 1 / 0 }), $(".s2-select-search").length > 0 && $(".s2-select-search").select2(), $(".s2-select-tags").length > 0 && $(".s2-select-tags").select2({ tags: !0 }) },
    bootstrap_daterange: function() { $(".daterange").length > 0 && $("input.daterange").daterangepicker(), $(".datetimerange").length > 0 && $("input.datetimerange").daterangepicker({ timePicker: !0, timePickerIncrement: 30, locale: { format: "MM/DD/YYYY h:mm A" } }) },
    bootstrap_datepicker: function() {
        $(".bs-datepicker").length > 0 && $(".bs-datepicker").datetimepicker({ format: "DD/MM/YYYY" }),
            $(".bs-datetimepicker").length > 0 && $(".bs-datetimepicker").datetimepicker(),
            $(".bs-timepicker").length > 0 && $(".bs-timepicker").datetimepicker({ format: "LT" }),
            $(".bs-datepicker-weekends").length > 0 && $(".bs-datepicker-weekends").datetimepicker({ format: "DD/MM/YYYY", daysOfWeekDisabled: [0, 6] }),
            $(".bs-datepicker-inline").length > 0 && $(".bs-datepicker-inline").datetimepicker({ inline: !0 }),
            $(".bs-datepicker-inline-time").length > 0 && $(".bs-datepicker-inline-time").datetimepicker({ inline: !0, sideBySide: !0 }),
            $(".bs-datepicker-inline-years").length > 0 && $(".bs-datepicker-inline-years").datetimepicker({ inline: !0, viewMode: "years" }),
            $(".bs-datepicker-inline-months").length > 0 && $(".bs-datepicker-inline-months").datetimepicker({ format: "MMMM YYYY", viewMode: "months" })
    },
    bootstrap_popover: function() { $("[data-toggle='popover']").popover(), $(".popover-hover").on("mouseenter", function() { $(this).popover("show") }).on("mouseleave", function() { $(this).popover("hide") }), $(".modal").on("show.bs.modal", function() { $("[data-toggle='popover']").popover("hide") }) },
    bootstrap_tooltip: function() { $("[data-toggle='tooltip']").tooltip() },
    maskedInput: function() { $("input[class^='mask_']").length > 0 && ($("input.mask_tin").mask("99-9999999"), $("input.mask_ssn").mask("999-99-9999"), $("input.mask_date").mask("9999-99-99"), $("input.mask_date_rev").mask("99-99-9999"), $("input.mask_product").mask("a*-999-a999"), $("input.mask_phone").mask("99 (999) 999-99-99"), $("input.mask_phone_ext").mask("99 (999) 999-9999? x99999"), $("input.mask_credit").mask("9999-9999-9999-9999"), $("input.mask_percent").mask("99%")) },
    noty: function() { $(".notify").on("click", function() { noty({ text: $(this).data("notify"), type: $(this).data("notify-type"), layout: $(this).data("notify-layout") ? $(this).data("notify-layout") : "topRight", animation: { open: "animated bounceIn", close: "animated fadeOut", speed: 200 } }) }) },
    datatables: function() { $(".datatable-basic").length > 0 && $(".datatable-basic").DataTable({ searching: !1, paging: !1, info: !1 }), $(".datatable-extended").length > 0 && $(".datatable-extended").DataTable() },
    knob: function() { $(".knob").length > 0 && $(".knob").knob({ format: function(t) { return t + "%" } }) },
    sparkline: function() { $(".sparkline").length > 0 && $(".sparkline").sparkline("html", { enableTagOptions: !0, disableHiddenCheck: !0 }) },
    wizard: function() { $(".wizard").length > 0 && ($(".wizard > ul").each(function() { $(this).addClass("steps_" + $(this).children("li").length) }), $(".wizard").smartWizard({ onLeaveStep: function(t) { var e = t.parents(".wizard"); if (e.hasClass("wizard-validation")) { var a = !0; if ($("input,textarea", $(t.attr("href"))).each(function(t, e) { a = validate.element(e) && a }), !a) return e.find(".stepContainer").removeAttr("style"), validate.focusInvalid(), !1 } return app.spy(), !0 }, onShowStep: function(t) { return t.parents(".wizard").hasClass("show-submit") && t.attr("rel") == t.parents(".anchor").find("li").length && t.parents(".wizard").find(".actionBar .btn-primary").css("display", "block"), app.spy(), !0 } })) },
    multiselect: function() {
        $(".multiselect").length > 0 && $(".multiselect").multiSelect({
            afterInit: function() {
                var t = this;
                t.$container.addClass("row"), t.$container.find(".ms-selectable, .ms-selection").addClass("col-xs-6")
            }
        })
    },
    bootstrap_colorpicker: function() { $(".bs-colorpicker").length > 0 && $(".bs-colorpicker").colorpicker({ sliders: { saturation: { maxLeft: 150, maxTop: 150 }, hue: { maxTop: 150 }, alpha: { maxTop: 150 } } }), $(".bs-colorpicker-lg").length > 0 && $(".bs-colorpicker-lg").colorpicker({ customClass: "colorpicker-2x", sliders: { saturation: { maxLeft: 250, maxTop: 250 }, hue: { maxTop: 250 }, alpha: { maxTop: 250 } } }) },
    loaded: function() { app_plugins.customScrollBar(), app_plugins.checkbox_radio(), app_plugins.formSpinner(), app_plugins.switch_button(), app_plugins.bootstrap_select(), app_plugins.select2(), app_plugins.bootstrap_popover(), app_plugins.bootstrap_datepicker(), app_plugins.bootstrap_tooltip(), app_plugins.maskedInput(), app_plugins.datatables(), app_plugins.knob(), app_plugins.sparkline(), app_plugins.isotope(), app_plugins.noty(), app_plugins.wizard(), app_plugins.bootstrap_daterange(), app_plugins.multiselect(), app_plugins.bootstrap_colorpicker() }
};
$(function() { app_plugins.loaded() }), $(document).ready(function() { app.loaded() });