
////////////////////////////////
// Primitive Helper Functions //
////////////////////////////////

String.prototype.format = function() {
  a = this;
  for (var k in arguments) {
    a = a.replace("{" + k + "}", arguments[k]);
  }
  return a;
};


function httpGetAsync(url, callback) {
    var xmlHttp = new XMLHttpRequest();
    xmlHttp.onreadystatechange = function() { 
        if (xmlHttp.readyState == 4 && xmlHttp.status == 200)
            callback(xmlHttp.responseText);
    };
    xmlHttp.open("GET", url, true); // true for asynchronous 
    xmlHttp.send(null);
}


function httpPostAsync(url, json, callback) {
    var xmlHttp = new XMLHttpRequest();
    xmlHttp.open("POST", url, true); // true for asynchronous 
    xmlHttp.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    xmlHttp.send(json);
    xmlHttp.onreadystatechange = function() { 
        if (xmlHttp.readyState == 4 && xmlHttp.status == 200)
            callback(xmlHttp.responseText);
    };
}


///////////////////////////
// More helper functions //
///////////////////////////

function ping() {
    httpGetAsync("/ping", function(data){
        localStorage.setItem("status", data);
    });
}


// function scanForDevices() {
//     httpGetAsync("/scan", function(data){
//         var devices = JSON.parse(data);
//         var html = "";
//         for (var i in devices) {
//             html += `
//             <button class="button button-primary cast-device">{0}</button>\n`.format(devices[i]);
//         }
//         console.log(html);
//     });   
// }


function loadMedia() {
    httpGetAsync("/media/list", function(data){
        localStorage.setItem("media", data);
        media = JSON.parse(data);
        var html = "";
        for (var i in media) {
            if (!$.isEmptyObject(media[i].history)) { // not empty
                html = buildHistoryHtml(media[i]) + html; // prepend for recent first
            }
        }
        $("#history").html(html);
    });
}


function buildHistoryHtml(data) {
    return `
            <div class="six columns">
              <a onclick="playFromHistory('{3}');" class="card no-shadow">
                <h6>{0}</h6>
                <p>{1} / {2}</p>
              </a>
            </div> <!--/columns-->\n`.format(data.title, data.history.current_time, 
                                             data.history.end_time, data.uuid);
}


function buildSearchResultsHtml(results) {
    var html = "";
    for (var i in results) {
        html += '<option value="{0}" data-title="{1}" data-uuid="{2}"></option>\n'.format(results[i].title, 
                                                                                          results[i].title, 
                                                                                          results[i].uuid);
    }
    return html;
}

function playFromHistory(uuid) {
    var json = JSON.stringify({"uuid":uuid});
    httpPostAsync("/play", json, function(data) {
        if (data.indexOf("Casting with args") != -1) {
            localStorage.setItem("status", "Playing");
        }
    });
}


////////////////
// DOM Loaded //
////////////////

$(document).ready(function() {

    /////////////////////
    // Click listeners //
    /////////////////////

    // Toggle device
    $("button.cast-device").click(function() {
        $("button.cast-device").each(function(i, obj) {
            $(obj).removeClass("button-primary");
        });
        $(this).addClass("button-primary");
        localStorage.setItem("device", this.value);
        var json = JSON.stringify({"device": this.value});
        httpPostAsync("select_device", json, function(data) {
            return 0;
        });
    });
    
    // Cast a file
    $("#cast-it").click(function() {
        var uuid = $("#media-list > option").data('uuid');
        var json = JSON.stringify({"uuid":uuid});
        httpPostAsync("/play", json, function(data) {
            if (data.indexOf("Casting with args") != -1) {
                localStorage.setItem("status", "Playing");
            }
        });

    });

    // Pause
    $("#pause-it").click(function() {
        httpGetAsync("/pause", function(data) {
            if (data.indexOf("pause") != -1) {
                localStorage.setItem("status", "Paused");
            }
        });
    });

    // Resume
    $("#resume-it").click(function() {
        httpGetAsync("/play", function(data) {
            if (data.indexOf("Resuming playback") != -1) {
                localStorage.setItem("status", "Playing");
            }
        });
    });

    // Search media
    $("#search-box").on("change paste keyup", function() {
        var maxResults = 10;
        var text = $(this).val();
        var media = JSON.parse(localStorage.getItem("media"));
        var options = {
            shouldSort: true,
            threshold: 0.6,
            location: 0,
            distance: 100,
            maxPatternLength: 32,
            minMatchCharLength: 1,
            keys: [
                "title"
            ]
        };
        var fuse = new Fuse(media, options);

        if (text.length > 2) {
            var result = fuse.search(text);
            var html = buildSearchResultsHtml(result.slice(0, maxResults));
            $("#media-list").html(html);
            // To access <option value="" data-uuid=""> use this: $("#media-list > option").data('uuid')
        }
    });

    ///////////
    // Setup //
    ///////////
    
    loadMedia();
    setInterval(function(){ ping(); }, 15000);



});
