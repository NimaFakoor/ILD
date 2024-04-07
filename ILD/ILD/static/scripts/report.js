const locationObj = {
    token: null,
    getLocation: function() {
        if(navigator.geolocation){
            const options = {
                enableHighAccuracy : true,
                timeout : Infinity,
                maximumAge : 0
            };
            navigator.geolocation.watchPosition(this.showPosition, this.showError, options);
        }
        else{
            document.getElementById('showLocation').innerHTML="Geolocation is not supported in your browser";
        }
    },

    getFormattedLatAndLng: function(coords) {
        return coords.longitude+ "," + coords.latitude;
    },

    getImageURL: function(coords) {
        return "https://api.mapbox.com/styles/v1/mapbox/streets-v11/static/" + 
            this.getFormattedLatAndLng(coords) +
            ",17.67,0.00,0.00/500x300@2x?access_token=" + this.token;
    },

    showPosition: function(position) {
        const imageURL = locationObj.getImageURL(position.coords);
        document.getElementById('showLocation').innerHTML = "<img src='" + imageURL + "' width=500 height=300>";        
        document.getElementById('mapUrl').innerHTML = imageURL;     
        document.getElementById('loc').innerHTML= '<br>عرض جغرافیایی: '+position.coords.latitude+'<br>طول جغرافیایی: '+position.coords.longitude;
        document.getElementById('speed').innerHTML= position.coords.speed;
        document.getElementById('height').innerHTML= position.coords.latitude;
    },

    showError: function(error) {
        switch(error.code) {
            case error.PERMISSION_DENIED:
                alert("User denied the request for Geolocation.");
                break;
            case error.POSITION_UNAVAILABLE:
                alert("Location information is unavailable.");
                break;
            case error.TIMEOUT:
                alert("The request to get user location timed out.");
                break;
            case error.UNKNOWN_ERROR:
                alert("An unknown error occurred.");
                break;
        }
    }
}

locationObj.token = "pk.eyJ1IjoiYXJhc2hyYXNvdWx6YWRlaCIsImEiOiJjanFjdzczNW8waTNmNDluMjl6eThoaHRjIn0.4z0bZqJRi8UQSLO2orkSjw";
locationObj.getLocation();


var marker = new mapboxgl.Marker()
  .setLngLat([30.5, 50.5])
  .addTo(locationObj.getLocation());