! function(i) {
    "use strict";

    function e() {
        this.$body = i("body"), this.charts = []
    }
    e.prototype.initCharts = function() {
        window.Apex = {
            chart: {
                parentHeightOffset: 0,
                toolbar: {
                    show: !1
                }
            },
            grid: {
                padding: {
                    left: 0,
                    right: 0
                }
            },
            colors: ["#727cf5", "#0acf97", "#fa5c7c", "#ffbc00"]
        };
        var e = new Date,
            t = function(e, t) {
                for (var a = new Date(t, e, 1), o = [], r = 0; a.getMonth() === e && r < 15;) {
                    var s = new Date(a);
                    o.push(s.getDate() + " " + s.toLocaleString("en-us", {
                        month: "short"
                    })), a.setDate(a.getDate() + 1), r += 1
                }
                return o
            }(e.getMonth() + 1, e.getFullYear()),
            a = ["#727cf5", "#0acf97", "#fa5c7c", "#ffbc00"];
        (n = i("#sessions-overview").data("colors")) && (a = n.split(","));
        var o = {
            chart: {
                height: 309,
                type: "area"
            },
            dataLabels: {
                enabled: !1
            },
            stroke: {
                curve: "smooth",
                width: 4
            },
            series: [{
                name: "Sessions",
                data: [10, 20, 5, 15, 10, 20, 15, 25, 20, 30, 25, 40, 30, 50, 35]
            }],
            zoom: {
                enabled: !1
            },
            legend: {
                show: !1
            },
            colors: a,
            xaxis: {
                type: "string",
                categories: t,
                tooltip: {
                    enabled: !1
                },
                axisBorder: {
                    show: !1
                },
                labels: {}
            },
            yaxis: {
                labels: {
                    formatter: function(e) {
                        return e + "k"
                    },
                    offsetX: -15
                }
            },
            fill: {
                type: "gradient",
                gradient: {
                    type: "vertical",
                    shadeIntensity: 1,
                    inverseColors: !1,
                    opacityFrom: .45,
                    opacityTo: .05,
                    stops: [45, 100]
                }
            }
        };
        
        for (var r = [], s = 10; 1 <= s; s--) r.push(s + " min ago");
        
        a = ["#727cf5", "#0acf97", "#fa5c7c", "#ffbc00"];
        (n = i("#country-chart").data("colors")) && (a = n.split(","));
        o = {
            chart: {
                height: 320,
                type: "bar"
            },
            plotOptions: {
                bar: {
                    horizontal: !0
                }
            },
            colors: a,
            dataLabels: {
                enabled: !1
            },
            series: [{
                name: "Sessions",
                data: [90, 75, 60, 50, 45, 36, 28, 20, 15, 12]
            }],
            xaxis: {
                categories: ["India", "China", "United States", "Japan", "France", "Italy", "Netherlands", "United Kingdom", "Canada", "South Korea"],
                axisBorder: {
                    show: !1
                },
                labels: {
                    formatter: function(e) {
                        return e + "%"
                    }
                }
            },
            grid: {
                strokeDashArray: [5]
            }
        };
        new ApexCharts(document.querySelector("#country-chart"), o).render();
        var n;
    }, e.prototype.initMaps = function() {
        0 < i("#world-map-markers").length && i("#world-map-markers").vectorMap({
            map: "world_mill_en",
            normalizeFunction: "polynomial",
            hoverOpacity: .7,
            hoverColor: !1,
            regionStyle: {
                initial: {
                    fill: "rgba(93,106,120,0.2)"
                }
            },
            series: {
                regions: [{
                    values: {
                        KR: "#e6ebff",
                        CA: "#b3c3ff",
                        GB: "#809bfe",
                        NL: "#4d73fe",
                        IT: "#1b4cfe",
                        FR: "#727cf5",
                        JP: "#e7fef7",
                        US: "#e7e9fd",
                        CN: "#8890f7",
                        IN: "#727cf5"
                    },
                    attribute: "fill"
                }]
            },
            backgroundColor: "transparent",
            zoomOnScroll: !1
        })
    }, e.prototype.init = function() {
        i("#dash-daterange").daterangepicker({
            singleDatePicker: !0
        }), this.initCharts(), this.initMaps(), window.setInterval(function() {
            var e = Math.floor(600 * Math.random() + 150);
            i("#active-users-count").text(e), i("#active-views-count").text(Math.floor(Math.random() * e + 200))
        }, 2e3)
    }, i.AnalyticsDashboard = new e, i.AnalyticsDashboard.Constructor = e
}(window.jQuery),
function() {
    "use strict";
    window.jQuery.AnalyticsDashboard.init()
}();