
var app = {};


/* Utils... */

app.get_date_string = function (epoch) {
    var dt = new Date(0);
    var month_dic = ["Xa", "Fe","Ma","Ap", "M", "Xñ", "Xl","Ag", "Se", "Ou", "No", "De"];
    dt.setUTCSeconds(epoch);
    return dt.getDate().toString() + month_dic[dt.getMonth()] + " " + dt.getHours().toString() + ":" + dt.getMinutes().toString();
};


/*Ajax...*/

app.get_info_from_ip = function (ip, callback){
    $.ajax({
        url: "cgi-bin/get_ip_info.py",
        data: {"ip": ip}
    }).done(function (data) {
        callback (false, data);
    }).fail(function() {
        console.log("Petition fails...");
        callback(true);
    });
};

app.get_connections = function (callback) {
    $.ajax({
        url: "cgi-bin/get_connections.py"
    }).done(function (data) {
        callback(false, data);
    }).fail(function () {
        console.log("Petition fails...");
        callback(true);
    });
};

app.get_last_connections = function (callback) {
    $.ajax({
        url: "cgi-bin/get_last_connections.py"
    }).done(function (data) {
        callback(false, data);
    }).fail(function () {
        console.log("Petition fails...");
        callback(true);
    });
};


/* Templates...*/

app.populate_connections = function (connections) {
    var html_body = Handlebars.templates.connections({"connections":connections});
    $("#web_body").html(html_body);
    app._end_reload();
};

app.populate_last_connections = function (last_connections) {
    html_body = Handlebars.templates.lastconnections({"connections":last_connections});
    $("#web_body").html(html_body);
};

app.populate_map_area = function () {

    Handlebars.registerHelper('connnum', function(arr) {
        return app.get_number_of_connections(arr);
    });

    Handlebars.registerHelper("sizeconn", app.get_size_connections);

    Handlebars.registerHelper('ifether', function(dev, opts) {
        if (dev.indexOf("eth") === 0){
            return opts.fn(this);
        } else {
            return opts.inverse(this);
        }
    });

    Handlebars.registerHelper('isenabled', function(ip,opts) {
        if (ip.valid_time === "0"){
            return opts.fn(this);
        } else {
            return opts.inverse(this);
        }
    });

    html_body = Handlebars.templates.networkmap({"connections":app.connections});
    $("#web_body").html(html_body);
};

app.populate_stats = function () {
    var ctx;

    var html_body = Handlebars.templates.historical({});
    $("#web_body").html(html_body);

    ctx = document.getElementById("historic_chart").getContext("2d");

    $.ajax({
        url: "cgi-bin/get_historical.py"
    }).done(function (data) {

        var x = Math.floor(data.length / 6);

        new Chart(ctx).Line({
            labels: data.map(function (item, index) {

                if  ((index !== data.length - 1 && (data[index + 1].time - data[index].time) > 2000) ||
                    (index !== 0 && (data[index].time - data[index - 1].time) > 2000) ||
                    (index % x === 0)){
                    return app.get_date_string(item.time);
                }

                return "";
            }),
            datasets: [{
                fillColor : "rgba(220,220,220,0.5)",
                strokeColor : "rgba(220,220,220,1)",
                pointColor : "rgba(220,220,220,1)",
                pointStrokeColor : "#fff",
                data : data.map(function (item) {return item.conns;})
            }]
        },
        {
            scaleShowLabels: true,
            scaleOverlay:true
        });

        app._end_reload();
    });
};


/* Helpers */

app.get_size_connections = function (dir, outgoing, incoming) {
    var size = 0;

    var direct = dir === "in" ? "size_in" : "size_out";

    if (outgoing) {
        for (var i = outgoing.length - 1; i >= 0; i--) {
            size += Number(outgoing[i][direct]);
        }
    }

    if (incoming) {
        for (var j = incoming.length - 1; j >= 0; j--) {
            size += Number(incoming[j][direct]);
        }
    }

    size = size * 1024;

    var mega = size / (1024*1024);
    var bites = size % (1024*1024);
    var kilo = bites / 1024;
    bites = bites % 1024;

    ret = "";

    if (Math.round(mega) !== 0){
        return Math.round(mega) + "MB ";
    }

    if (Math.round(kilo) !== 0){
        return Math.round(kilo) + "KB ";
    }

    return Math.round(bites) + "B";
};

app.get_number_of_connections = function (conns) {
    var ret = 0;

    if (! conns) return 0;

    for (var i = conns.length - 1; i >= 0; i--) {
        if (conns[i].number === 0) {
            ret++;
        } else {
            ret += conns[i].number;
        }
    }
    return ret;
};


/* Reload... */

app._start_reload = function () {
    $("#reload_main_icon").addClass("icon-spin");
};

app._end_reload =function  () {
    $("#reload_main_icon").removeClass("icon-spin");
};

app.reload = function () {
    var fun_dic;
    app._start_reload();
    fun_dic = {
            "stats_tab": app.populate_stats,
            "map_tab": app.reload_map_tab,
            "last_conns_tab": app.reload_last_connections};
    fun_dic[app.enabled_tab]();
};

app.reload_stats_tab = function (argument) {
};

app.reload_map_tab = function () {
    app.get_connections(function (fail, data) {

        if (fail){
            console.log("MERDA1!!");
            return;
        }

        app.connections = data;
        app.populate_map_area();
        app._end_reload();
    });
};

app.reload_last_connections = function() {
    app.get_last_connections(function (fail, data) {
        if (fail) {
            console.log("MERDA2!!")
        }

        app.populate_last_connections(data);
        app._end_reload();
    });
};


/* Enable tabs... */

app._enable_tab_function_creator = function (id) {
    return function () {
        app.enabled_tab = id;
        $("l-nav ul li").removeClass("active");
        $("li#" + id).addClass("active");
        app.reload();
    };
};

app.enable_stats_tab = app._enable_tab_function_creator("stats_tab");
app.enable_network_map_tab = app._enable_tab_function_creator("map_tab");
app.enable_last_connections_tab = app._enable_tab_function_creator("last_conns_tab");

app.enable_ip_info = function (ip) {
    var ip_info = app.connections[ip];

    var out_conn = ip_info["Outgoing"];
    var inc_conn = ip_info["Incoming"];

    var html_body = Handlebars.templates.ipinfo(
        {"ip": ip,
         "incoming_conn": app.get_number_of_connections(inc_conn),
         "outgoing_conn": app.get_number_of_connections(out_conn)});
    $("#web_body").html(html_body);

    app.enable_ip_info_tab(ip, "Outgoing");
};

app.enable_ip_info_tab = function (ip, direction){
    var ip_info = app.connections[ip];
    var is_incoming = direction === "Incoming";

    var html_body = Handlebars.templates.connections({"connections": ip_info[direction], "incoming": is_incoming});
    $("#ip_info_body").html(html_body);
};

app.show_ip_connection_details = function (id, ip) {
    $("#conn" + id + " .more").slideToggle("slow");

    app.get_info_from_ip(ip, function(fail,  data) {
        var html_body = Handlebars.templates.connectiondetails({"info": data})
        $("#conn" + id + " .more").html(html_body);
    });
};

app.show_ip_last_connection_details = function (id, ip_origen, ip_dest){

    $("#conn" + id + " .more").slideToggle("slow");

    app.get_info_from_ip(ip_origen, function(fail,  data_origen) {
        app.get_info_from_ip(ip_dest, function(fail,  data_dest) {
            var html_body = Handlebars.templates.connectiondetails2ips({"origen": data_origen, "destino": data_dest});
            $("#conn" + id + " .more").html(html_body);
        });
    });

};

$(document).ready(app.enable_network_map_tab);