var dgram = require("dgram") ;
var crypto = require("crypto") ;
var fs = require("fs") ;

function packageCollector(package_src_ip, payload_size, now) {

  this.rcvPackage = function (now) {
    this.watchdog_timer = now ;
    this.packet_counter++ ;

    switch (this.packet_counter) {
     // transmission of packet 20 starts
     case 20:
       this.start_timer = now ;
       break ;
     // got 50 more packages
     case 70:
       this.end_timer = now ;
       this.logTimingResults() ;
       this.init() ;
       break ;
    }
  }

  this.logTimingResults = function () {
    var transmission_time = this.end_timer - this.start_timer ;
    var bitrate = (this.size * 400000) / transmission_time ;
    var size = this.size ;

    console.log("Got 50 packages from " + this.ip + " of " + this.size + "b in " + transmission_time + "ms") ;
    console.log("This implies a payload bitrate of: " + bitrate + "b/s") ;

    // Log to file
    var stream = fs.createWriteStream("./logs/" + this.ip + ".dat", { 'flags': 'a' }) ;
    stream.once('open', function(fd) {
      stream.write(size + "\t" + bitrate + "\n") ;
      stream.end() ;
    }) ;
  }

  this.init = function (now) {
    this.watchdog_timer = now ;
    this.packet_counter = 0 ;
    this.start_timer = 0 ;
    this.end_timer = 0 ;
  }

  this.ip = package_src_ip ;
  this.size = payload_size ;
  this.init(now) ;
  this.packet_counter++ ;
}

function Watchdog() {
  global.collectorList = new Array() ;

  // add a heartbeat function to packageCollector objects
  packageCollector.prototype.isAllive = function() {
    return (new Date().getTime() - 1000 < this.watchdog_timer) ;
  }

  function watch() {
    var i = 0 ;
    while (i < global.collectorList.length) {
      if (!global.collectorList[i].isAllive()) {
        var collector = global.collectorList[i] ;
        // don't trust the garbage collector
        collector.init() ;
        global.collectorList = global.collectorList.splice(i, i) ;
        collector_n = createCollectorName(collector.ip, collector.size) ;
        global[collector_n] = null ;
      } else i++ ;
    }
  }

  this.addCollector = function(collector) {
    global.collectorList.push(collector) ;
  }

  setInterval(watch, 1000) ;
  console.log("INFO: starting the watchdog") ;
}

function createCollectorName(ip, size) {
  var sha1 = crypto.createHash('sha1') ;
  sha1.update(ip + size) ;
  return (sha1.digest('hex') + "_Collector") ;
}

var server = dgram.createSocket("udp4") ;

server.on("message", function (msg, rinfo) {

  var payload_size = msg.length ;

  var now = new Date().getTime() ;

  var collector = createCollectorName(rinfo.address, payload_size) ;

  try {
    global[collector].rcvPackage(now) ;
  } catch (e) {
    if (e.type == 'non_object_property_call') {
      console.log("INFO: create new packageCollector #" + collector) ;
      global[collector] = new packageCollector(rinfo.address, payload_size, now) ;
      hasso_the_dog.addCollector(global[collector]) ;
    } else {
      throw(e) ;
    }
  }
});



server.on("listening", function () {
  var address = server.address();
  hasso_the_dog = new Watchdog() ;
  console.log("INFO: speed server listening " +
      address.address + ":" + address.port);
});

server.bind(12312);
