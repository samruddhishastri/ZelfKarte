function onScanSuccess(qrCodeMessage) {
	console.log('Scan Successful'); 
}

var html5QrcodeScanner = new Html5QrcodeScanner(
	"reader", { fps: 10, qrbox: 250 });
html5QrcodeScanner.render(onScanSuccess);

function myFunction_signup() {
  	var x = document.getElementById("passwd");
  	if (x.type === "password") {
    	x.type = "text";
  	} 
  	else {
    	x.type = "password";
  	}
}


function myFunction_login() {
  	var x = document.getElementById("passwd");
  	if (x.type === "password") {
    	x.type = "text";
  	} 
  	else {
    	x.type = "password";
  	}
}