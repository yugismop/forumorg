$(function() {
    //Initialize Select2 Elements
    $(".select2").select2({
        language: "fr"
    });
    $("#datetime").inputmask("datetime", {
        "placeholder": "jj/mm/aaaa hh:ss"
    });
    var options = {
        autoPlaceholder: "aggressive",
        dropdownContainer: "body",
        geoIpLookup: function(callback) {
            $.get("http://ipinfo.io", function() {}, "jsonp").always(function(resp) {
                var countryCode = (resp && resp.country) ?
                    resp.country :
                    "";
                callback(countryCode);
            });
        },
        placeholderNumberType: "MOBILE",
        initialCountry: "auto",
        preferredCountries: [
            'fr', 'ch', 'be', 'ma', 'nl'
        ],
        utilsScript: "https://cdnjs.cloudflare.com/ajax/libs/intl-tel-input/11.0.0/js/utils.js"
    };
    $("#phone").intlTelInput(options);
    $("#phone_stand").intlTelInput(options);
    options.placholderNumberType = "FIXED_LINE";
    $("#phone_facturation").intlTelInput(options);
    $("#persons").inputmask("9", {
        "placeholder": "x"
    });
    $('#banner').editable({
        mode: 'inline',
        emptytext: 'Ajoutez votre bannière',
        error: function(response, newValue) {
            if (response.status == 500) {
                return 'Impossible à modifier (section validée).';
            } else {
                return response.responseText;
            }
        }
    });
    $('.section').click(function(e) {
        e.preventDefault();
        validate_section();
        return false;
    });
});
