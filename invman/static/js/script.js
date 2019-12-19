$(document).ready(function(){
    var locId = ''
    var prod = $('#choose-product').val().split(',')[0] // used by getQuantity()
    var loc = $('#select-location').val().split(',')[0] // used by getQuantity()
    var moveTos = [];
    
    function updateMoveTo(l){
        var updatedMoveTos = [];
        $.each(moveTos, function(index){
            
            if (moveTos[index] != l) {
                updatedMoveTos.push(moveTos[index])
            }
            
        })
        
        $('#move-to').find('option').remove();
        $.each(updatedMoveTos, function(index){
            var opt_item = '<option value="' + updatedMoveTos[index] + '">' + updatedMoveTos[index] + '</option>'
            $('#move-to').append(opt_item);
        })
        
    }

    function getQuantity(prd, lo){
        var xhttp = new XMLHttpRequest();
        xhttp.onreadystatechange = function(){
            if (xhttp.readyState == 4 && xhttp.status == 200) {
                data = JSON.parse(xhttp.responseText);
                document.getElementById('qty-disp').innerHTML = "Available: "+data['qty'];
            }
        }
        xhttp.open('GET', '/main/_getquantity/' + prd + '/' + lo, true);
        xhttp.send();
    }
    
    function updateQuantity(){
        prod = $('#choose-product').val().split(',')[0]
        loc = $('#select-location').val().split(',')[0]
        getQuantity(prod, loc)
    }

    function getResponse(){
        var xhttp = new XMLHttpRequest();
        xhttp.onreadystatechange = function(){
            if (xhttp.readyState == 4 && xhttp.status == 200) {
                data = JSON.parse(xhttp.responseText);
                $('#choose-product').find('option').remove();
                $.each(data, function(key, val){
                    var option_item = '<option value="' + key + '">' + key + ', ' + val + '</option>'
                    $('#choose-product').append(option_item);
                    updateQuantity();
                })
            }
        }
        xhttp.open('GET', '/main/_loadproducts/' + locId.split(',')[0], true);
        xhttp.send();
    }
    
    // Set available quantity for product.
    getQuantity(prod, loc)

    // Push MoveTo locations to moveTos
    $("#move-to > option").each(function(){
        moveTos.push(this.value)
    })

    // Functions to dynamically change products & available quantity based on location selected
    $('#choose-product').change(function(){
        prod = $('#choose-product').val().split(',')[0]
        loc = $('#select-location').val().split(',')[0]
        getQuantity(prod, loc)
    })
    $('#select-location').change(function(){
        locId = $(this).val();
        getResponse();
        updateMoveTo(locId);
    })
})


