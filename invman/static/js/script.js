$(document).ready(function(){

    // Gets the quantity of a product at a particular location.
    function getQuantity(prd, lo, op){
        var xhttp = new XMLHttpRequest();
        xhttp.onreadystatechange = function(){
            if (xhttp.readyState == 4 && xhttp.status == 200) {
                data = JSON.parse(xhttp.responseText);
                if (op == 'purchase') {
                    document.getElementById('qty-disp-purchase').innerHTML = "Available: "+data['qty'];
                }
                else if (op == 'sales') {
                    document.getElementById('qty-disp-sales').innerHTML = "Available: "+data['qty'];
                }
                else if (op == 'movement') {
                    document.getElementById('qty-disp-movement').innerHTML = "Available: "+data['qty'];
                }
            }
        }
        xhttp.open('GET', '/main/_getquantity/' + prd + '/' + lo, true);
        xhttp.send();
    }

    // Gets products at a particular location
    function getResponse(locId, op){
        var xhttp = new XMLHttpRequest();
        xhttp.onreadystatechange = function(){
            if (xhttp.readyState == 4 && xhttp.status == 200) {
                data = JSON.parse(xhttp.responseText);
                if (op == 'sales') {
                    $('#sales-product').find('option').remove();
                    $.each(data, function(key, val){
                        var option_item = '<option value="' + key + '">' + key + ', ' + val + '</option>'
                        $('#sales-product').append(option_item);
                    })
                    updateSales();
                }
                if (op == 'movement') {
                    $('#product-to-move').find('option').remove();
                    $.each(data, function(key, val){
                        var option_item = '<option value="' + key + '">' + key + ', ' + val + '</option>'
                        $('#product-to-move').append(option_item);
                    })
                    updateMovements();
                }
            }
        }
        xhttp.open('GET', '/main/_loadproducts/' + locId, true);
        xhttp.send();
    }

    function updateMoveTo(l){
        var moveTos = [];
        $("#move-purchase > option").each(function(){
            moveTos.push(this.value);
        })
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

    function toggleOperations(op){
        if (op == 'Purchase') {
            $('#movement-operation').hide();
            $('#sales-operation').hide();
            $('#purchase-operation').show();
        }
        else if (op == 'Sales') {
            $('#movement-operation').hide();
            $('#sales-operation').show();
            $('#purchase-operation').hide();
        }
        else if (op == 'Movement') {
            $('#movement-operation').show();
            $('#sales-operation').hide();
            $('#purchase-operation').hide();
        }
    }

    function updateSales() {
        var prodSales = $('#sales-product').val().split(',')[0];
        getQuantity(prodSales, locSales, 'sales');
    }

    function updateMovements() {
        var lc = $('#move-from').val().split(',')[0];
        var prd = $('#product-to-move').val().split(',')[0];
        getQuantity(prd, lc, 'movement');
    }

    var opr = $('#operations').val();
    toggleOperations(opr);
    $('#operations').change(function(){
        opr = $('#operations').val();
        toggleOperations(opr);
    })

    // Dynamic functionality for purchase operation 
    var prodPurchase = $('#purchase-product').val().split(',')[0];
    getQuantity(prodPurchase, 'Product Factory', 'purchase');
    $('#purchase-operation').change(function(){
        prodPurchase = $('#purchase-product').val().split(',')[0];
        getQuantity(prodPurchase, 'Product Factory', 'purchase');
    })

    // Dynamic functionality for sales operation
    var locSales = $('#sales-location').val().split(',')[0];
    getResponse(locSales, 'sales');
    $('#sales-location').change(function(){
        locSales = $('#sales-location').val().split(',')[0];
        getResponse(locSales, 'sales');
    })
    $('#sales-product').change(function(){
        updateSales();
    })

    // Dynamic functionality for movement operation
    
    var loc = $('#move-from').val()
    updateMoveTo(loc);
    getResponse(loc.split(',')[0], 'movement')
    $('#move-from').change(function(){
        updateMoveTo($('#move-from').val());
        getResponse($('#move-from').val().split(',')[0], 'movement')
    })
    $('#product-to-move').change(function(){
        updateMovements();
    })
})