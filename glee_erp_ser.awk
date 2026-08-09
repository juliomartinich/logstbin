# Julio Martinich 1-oct-2024
# glee_erp_ser.awk lee los archivos log erp Server
# v1  1-oct-24 basado en el lector de telematics server
#
# para correr este script primero se debe hacer 
# chmod +x glee_erp_ser.awk
#
# awk -f glee_erp_ser.awk {archivo log} > erp_ser.csv      --- deja el resultado en erp_ser.csv
#
# en mi mac uso gawk y funciona
# GNU Awk 5.3.1, API 4.0, PMA Avon 8-g1, (GNU MPFR 4.2.1, GNU MP 6.3.0)
#
# el bloque BEGIN se ejecuta una sola vez, lo uso para poner los titulos, con ; para que sea un archivo csv leible en excel
BEGIN { 
   print "log;fechahora;mseg;tipo;numero;tiponum;host;metodo;api;apisola;version;httpstatus;syncrotessDeliveryNumber;detail;orderNo;soldtoname;soldtonum;shiptoname;shiptonum;street;postcode;city;latitude;longitude;minQuantity;maxQuantity;dateTimeEarliestFirstLoadOnCustomerSite;dateTimeLatestFirstLoadOnCustomerSite;principalPlant;productId;deliveryType;deliveryQuantity;erpTicketNumber;truckId;truckName;truckType;parkingLocation;homeLocation;licensePlate;raw";
}
function utc_to_clt(fecha_in, hora_in,    f, h, str_utc, epoch, fecha_local, hora_local, mseg) {
    split(fecha_in, f, /[\/-]/);
    split(hora_in, h, /[:.]/);
    mseg = (length(h[4]) > 0) ? h[4] : "000";

    ENVIRON["TZ"] = "UTC";
    str_utc = sprintf("%04d %02d %02d %02d %02d %02d", f[1], f[2], f[3], h[1], h[2], h[3]);
    epoch = mktime(str_utc);

    ENVIRON["TZ"] = "America/Santiago";
    fecha_local = strftime("%Y/%m/%d", epoch);
    hora_local  = strftime("%H:%M:%S", epoch);

    return fecha_local " " hora_local ";" mseg;
}

#
# este bloque se ejecuta para cada línea de entrada, $0 es la línea completa, $1, $2, ... son los tokens separados por espacio
{   
    # Extracción de algunos campos directamente por su ubicacion en el archivo
    # las ubicaciones las vi directamente inspeccionando el archivo

    # si ay lineas que vienen con ctrl-M, las limpio
    linea = $0;
    gsub(/\r/,"",linea)

    # solamente me interesan los mensaje 120 (recepcion) y 125 (respuesta)
    # en el mensaje 120 recupero las variables, y luego en el 125 veo si salió exitoso
    if ( match(linea, /120 ==/ )) {
        tiponum = 120;
        fechahora = utc_to_clt($1, $2);
        tipo = $8;
        numero = $10;

        detail = "";
        # Extrae la parte después de "120 =="
        result = substr(linea, RSTART + RLENGTH);
        # Divide el resultado en tokens separados por espacios
        split(result, tokens, " ");
        metodo = tokens[1];
        api = tokens[2]; 

        # extraigo  la apisola todo lo que no sea / después de erp
        if (match(api, /\/erp\/([^\/]+)/, resultado)) {
            apisola = resultado[1];
        } else { apisola = ""; }

        # extraigo el numero de ticket syncrotess si viene así: /webservices/erp/delivery/20241007_418866.1_004
        if (match(api, /\/webservices\/erp\/delivery\/([^"]+)/, resultado)) {
            stdnapi = resultado[1];
        } else { stdnapi = ""; }

        # la funcion match la uso sobre $0 que es la linea leida completa
        # el resultado de lo encontrado en la expresion regular queda en un array 
        # para cada exoresion en parentesis redondos () hay un resultado 
        # el primer dato del array es el que tiene el primer resultado (en este caso uno solo)
        # voy obteniendo los datos del string uno por uno

        # Host con H mayuscula expresion regular de una IP
        if (match(linea, /Host: ([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})/, resultado)) {
            host = resultado[1];
            } else { host = ""; }
    
        # Version (lo que está entre comillas y que no sea comillas)
        if (match(linea, /"version"[[:space:]]*:[[:space:]]*"([^"]+)"/, resultado)) {
            ver = resultado[1];
        } else { ver = ""; }
    
        # Busca orderNumber
        # expresion regular: obtenga lo que esté entre comillas, y que no sea comillas
        if (match(linea, /"orderNumber"[[:space:]]*:[[:space:]]*"([^"]+)"/, resultado)) {
            onum = resultado[1];
        } else { onum = ""; }
    
        # Busca soldToName
        # expresion regular: obtenga lo que esté entre comillas, y que no sea comillas
        if (match(linea, /"soldToName"[[:space:]]*:[[:space:]]*"([^"]+)"/, resultado)) {
            soldtoname = resultado[1];
        } else { soldtoname = ""; }
    
        # Busca soldToNum
        # expresion regular: obtenga lo que esté entre comillas, y que no sea comillas
        if (match(linea, /"soldToNum"[[:space:]]*:[[:space:]]*"([^"]+)"/, resultado)) {
            soldtonum = resultado[1];
        } else { soldtonum = ""; }
    
        # Busca shipToName
        # expresion regular: obtenga lo que esté entre comillas, y que no sea comillas
        if (match(linea, /"shipToName"[[:space:]]*:[[:space:]]*"([^"]+)"/, resultado)) {
            shiptoname = resultado[1];
        } else { shiptoname = ""; }
    
        # Busca shipToNum
        # expresion regular: obtenga lo que esté entre comillas, y que no sea comillas
            if (match(linea, /"shipToNum"[[:space:]]*:[[:space:]]*"([^"]+)"/, resultado)) {
        shiptonum = resultado[1];
        } else { shiptonum = ""; }
    
        # street (lo que está entre comillas y que no sea comillas)
        if (match(linea, /"street"[[:space:]]*:[[:space:]]*"([^"]+)"/, resultado)) {
            street = resultado[1];
        } else { street = ""; }
    
        # postcode (lo que está entre comillas y que no sea comillas)
        if (match(linea, /postcode"[[:space:]]*:[[:space:]]*"([^"]+)"/, resultado)) {
            postcode = resultado[1];
        } else { postcode = ""; }
    
        # city (lo que está entre comillas y que no sea comillas)
        if (match(linea, /city"[[:space:]]*:[[:space:]]*"([^"]+)"/, resultado)) {
        city = resultado[1];
        } else { city = ""; }
    
        # latitude (lo que está entre comillas y que no sea comillas)
        if (match(linea, /latitude"[[:space:]]*:[[:space:]]*"([^"]+)"/, resultado)) {
            latitude = resultado[1];
            gsub(/\./, ",", latitude);
        } else { latitude = ""; }

        # longitude (lo que está entre comillas y que no sea comillas)
        if (match(linea, /longitude"[[:space:]]*:[[:space:]]*"([^"]+)"/, resultado)) {
            longitude = resultado[1];
            gsub(/\./, ",", longitude);
        } else { longitude = ""; }

        # minQuantity (lo que está entre comillas y que no sea comillas)
        if (match(linea, /minQuantity"[[:space:]]*:[[:space:]]*([0-9]+)/, resultado)) {
            minQuantity = resultado[1];
        } else { minQuantity = ""; }
    
        # maxQuantity (lo que está entre comillas y que no sea comillas)
        if (match(linea, /maxQuantity"[[:space:]]*:[[:space:]]*([0-9]+)/, resultado)) {
            maxQuantity = resultado[1];
        } else { maxQuantity = ""; }
    
        # dateTimeEarliestFirstLoadOnCustomerSite (lo que está entre comillas y que no sea comillas)
        if (match(linea, /dateTimeEarliestFirstLoadOnCustomerSite"[[:space:]]*:[[:space:]]*"([^"]+)"/, resultado)) {
            dateTimeEarliestFirstLoadOnCustomerSite = resultado[1];
        } else { dateTimeEarliestFirstLoadOnCustomerSite = ""; }
    
        # dateTimeLatestFirstLoadOnCustomerSite (lo que está entre comillas y que no sea comillas)
        if (match(linea, /dateTimeLatestFirstLoadOnCustomerSite"[[:space:]]*:[[:space:]]*"([^"]+)"/, resultado)) {
            dateTimeLatestFirstLoadOnCustomerSite = resultado[1];
        } else { dateTimeLatestFirstLoadOnCustomerSite = ""; }

        # principalPlant (lo que está entre comillas y que no sea comillas)
        if (match(linea, /principalPlant"[[:space:]]*:[[:space:]]*"([^"]+)"/, resultado)) {
            principalPlant = resultado[1];
        } else { principalPlant = ""; }

        # productIdD (lo que está entre comillas y que no sea comillas)
        if (match(linea, /productId"[[:space:]]*:[[:space:]]*"([^"]+)"/, resultado)) {
            productId = resultado[1];
        } else { productId = ""; }

        # deliveryType (lo que está entre comillas y que no sea comillas)
        if (match(linea, /deliveryType"[[:space:]]*:[[:space:]]*"([^"]+)"/, resultado)) {
            deliveryType = resultado[1];
        } else { deliveryType = ""; }

        # deliveryQuantity (lo que está entre comillas y que no sea comillas)
        if (match(linea, /deliveryQuantity"[[:space:]]*:[[:space:]]*([0-9]+\.[0-9]+)/, resultado)) {
            deliveryQuantity = resultado[1];
            gsub(/\./, ",", deliveryQuantity);
        } else { deliveryQuantity = ""; }

        # erpTicketNumber (lo que está entre comillas y que no sea comillas)
        if (match(linea, /erpTicketNumber"[[:space:]]*:[[:space:]]*"([^"]+)"/, resultado)) {
            erpTicketNumber = resultado[1];
        } else { erpTicketNumber = ""; }

        #------------- /webservices/erp/truck

        # truckId (lo que está entre comillas y que no sea comillas)
        if (match(linea, /truckId"[[:space:]]*:[[:space:]]*"([^"]+)"/, resultado)) {
            truckId = resultado[1];
        } else { truckId = ""; }

        # truckName (lo que está entre comillas y que no sea comillas)
        if (match(linea, /truckName"[[:space:]]*:[[:space:]]*"([^"]+)"/, resultado)) {
            truckName = resultado[1];
        } else { truckName = ""; }
    
        # truckType (lo que está entre comillas y que no sea comillas)
        if (match(linea, /truckType"[[:space:]]*:[[:space:]]*"([^"]+)"/, resultado)) {
            truckType = resultado[1];
        } else { truckType = ""; }
    
        # parkingLocation (lo que está entre comillas y que no sea comillas)
        if (match(linea, /parkingLocation"[[:space:]]*:[[:space:]]*"([^"]+)"/, resultado)) {
            parkingLocation = resultado[1];
        } else { parkingLocation = ""; }
    
        # homeLocation (lo que está entre comillas y que no sea comillas)
        if (match(linea, /homeLocation"[[:space:]]*:[[:space:]]*"([^"]+)"/, resultado)) {
            homeLocation = resultado[1];
        } else { homeLocation = ""; }
    
        # licensePlate (lo que está entre comillas y que no sea comillas)
        if (match(linea, /licensePlate"[[:space:]]*:[[:space:]]*"([^"]+)"/, resultado)) {
            licensePlate = resultado[1];
        } else { licensePlate = ""; }
    
        #------------- /webservices/erp/delivery/SignOff
        raw = linea
        gsub(/;/,"|",raw)
        # me quedo con las variables guardadas y voy a la siguiente linea, que debe ser la respuesta
        next;
    }
 
    #ahora leo la respuesta e imprimo

    if ( match(linea, /125 ==/ )) {
        # Extrae la parte después de "125 =="
        result = substr(linea, RSTART + RLENGTH);
        # Divide el resultado en tokens separados por espacios
        split(result, tokens, " ");
        cod_respuesta = tokens[2];
        respuesta     = tokens[3];
        httpstatus = cod_respuesta " " respuesta;
        # debo parsear "detail" : []
        if (match(result, /"detail"[[:space:]]:[[:space:]](\[.*\])/, resultado)) {
            detail = resultado[1];
            gsub(/;/, ":", detail)
        } else { detail = "" }
        # imprimo en una linea todos los datos separados por ; para que funcione como archivo csv
        print "SEi;" fechahora ";" tipo ";" numero ";" tiponum ";" host ";" metodo ";" api ";" apisola ";" ver ";" httpstatus ";" stdnapi ";" detail ";" onum ";" soldtoname ";" soldtonum ";" shiptoname ";" shiptonum ";" street ";" postcode ";" city ";" latitude ";" longitude ";" minQuantity ";" maxQuantity ";" dateTimeEarliestFirstLoadOnCustomerSite ";" dateTimeLatestFirstLoadOnCustomerSite ";" principalPlant ";" productId ";" deliveryType ";" deliveryQuantity ";" erpTicketNumber ";" truckId ";" truckName ";" truckType ";" parkingLocation ";" homeLocation ";" licensePlate ";" raw;
    }

}
