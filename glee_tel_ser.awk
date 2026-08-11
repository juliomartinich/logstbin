# Julio Martinich
# lee archivos log de syncrotess de telemetria Server
# 29-sep-2024 primera version
#  1-oct      le cambio el nombre y leo todo el archivo sin necesidad de primero hacer grep body
# 
# para correr este script primero se debe hacer 
# chmod +x glee_tel_ser.awk
#
# Opciones de hora:
# awk -v tz=UTC -f glee_tel_ser.awk {archivo log tel server} > tel_ser.csv      --- convierte UTC a CLT (default)
# awk -v tz=CLT -f glee_tel_ser.awk {archivo log tel server} > tel_ser.csv      --- no convierte la hora (CLT)
#
# en mi mac uso gawk y funciona
# GNU Awk 5.3.1, API 4.0, PMA Avon 8-g1, (GNU MPFR 4.2.1, GNU MP 6.3.0)
#
# el bloque BEGIN se ejecuta una sola vez, lo uso para poner los titulos, con ; para que sea un archivo csv leible en excel
BEGIN { print "log;fechahora;mseg;tipo;numero;tiponum;metodo;host;host2;api;apisola;version;httpstatus;timeStamp;subOrgID;licensePlate;syncrotessDeliveryNumber;status;statusSource;latitude;longitude;eta;productAmount;leftOverAmount;mess;raw"; }
function format_time(fecha_in, hora_in,    f, h, str_utc, epoch, fecha_local, hora_local, mseg) {
    split(fecha_in, f, /[\/-]/);
    split(hora_in, h, /[:.]/);
    mseg = (length(h[4]) > 0) ? h[4] : "000";

    if (tz == "CLT") {
        return sprintf("%04d/%02d/%02d %02d:%02d:%02d;%s", f[1], f[2], f[3], h[1], h[2], h[3], mseg);
    } else {
        ENVIRON["TZ"] = "UTC";
        str_utc = sprintf("%04d %02d %02d %02d %02d %02d", f[1], f[2], f[3], h[1], h[2], h[3]);
        epoch = mktime(str_utc);

        ENVIRON["TZ"] = "America/Santiago";
        fecha_local = strftime("%Y/%m/%d", epoch);
        hora_local  = strftime("%H:%M:%S", epoch);

        return fecha_local " " hora_local ";" mseg;
    }
}

#
# este bloque se ejecuta para cada línea de entrada, $0 es la línea completa, $1, $2, ... son los tokens separados por espacio
{   
    # Extracción de algunos campos directamente por su ubicacion en el archivo
    # las ubicaciones las vi directamente inspeccionando el archivo
    linea = $0;
    gsub(/\r/,"",linea)

    # solamente me interesan los mensaje 120 (recepcion) y 125 (respuesta)
    if ( match(linea, /120 ==/ )) {
        tiponum = 120;
        fechahora = format_time($1, $2);
        tipo = $8;
        numero = $10;

        # Extrae la parte después de "120 =="
        result = substr(linea, RSTART + RLENGTH);
        # Divide el resultado en tokens separados por espacios
        split(result, tokens, " ");
        metodo  = tokens[1];
        api     = tokens[2];
        if (match(api, /\/webservices\/telematics\/([^, "?]+)/, resultado)) {
            apisola = resultado[1];
        } else { apisola = ""; }

        # Host con H mayuscula
        if (match(linea, /Host:[[:space:]]*([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})/, resultado)) {
            host = resultado[1];
        } else { host = ""; }
    
        # host en minusculas
        if (match(linea, /host:[[:space:]]*([^;\]]+)/, resultado)) {
            host2 = resultado[1];
        } else { host2 = ""; }

        # Busca syncrotessDeliveryNumber
        if (match(linea, /"syncrotessDeliveryNumber"[[:space:]]*:[[:space:]]*"([^"]+)"/, resultado)) {
            stn = resultado[1];
        } else { stn = ""; }

        # sttVersion
        if (match(linea, /"sttVersion"[[:space:]]*:[[:space:]]*"([^"]+)"/, resultado)) {
            ver = resultado[1];
        } else { ver = ""; }
    
        # timeStamp
        if (match(linea, /"timeStamp"[[:space:]]*:[[:space:]]*"([^"]+)"/, resultado)) {
            ts = resultado[1];
        } else { ts = ""; }
    
        # subOrgID
        if (match(linea, /"subOrgID"[[:space:]]*:[[:space:]]*"([^"]+)"/, resultado)) {
            soi = resultado[1];
        } else { soi = ""; }
    
        # vehicleNumber
        if (match(linea, /"vehicleNumber"[[:space:]]*:[[:space:]]*"([^"]+)"/, resultado)) {
            vn = resultado[1];
        } else { vn = ""; }
    
        # status
        if (match(linea, /"status"[[:space:]]*:[[:space:]]*"([^"]+)"/, resultado)) {
            st = resultado[1];
        } else { st = ""; }
    
        # statusSource
        if (match(linea, /"statusSource"[[:space:]]*:[[:space:]]*"([^"]+)"/, resultado)) {
            sts = resultado[1];
        } else { sts = ""; }
    
        # messageText
        if (match(linea, /"messageText"[[:space:]]*:[[:space:]]*"([^"]+)"/, resultado)) {
            mess = resultado[1];
            gsub(/;/, "", mess);
        } else { mess = ""; }
    
        # eta
        if (match(linea, /"eta"[[:space:]]*:[[:space:]]*"([^"]+)"/, resultado)) {
            eta = resultado[1];
        } else { eta = ""; }
    
        # productQuantityActual
        if (match(linea, /"productQuantityActual"[[:space:]]*:[[:space:]]*\{([^}]*)\}/, resultado)) {
            pqa = resultado[1];
            if (match(pqa, /"amount"[[:space:]]*:[[:space:]]*([0-9.]+)/, resultado)) {
                amount = resultado[1];
                gsub(/\./, ",", amount)
            } else {
                amount = "";
            }
        } else {
            pqa = "";
            amount = "";
        }
    
        # leftOver
        if (match(linea, /"leftOver"[[:space:]]*:[[:space:]]*\{([^}]*)\}/, resultado)) {
            lo = resultado[1];
            if (match(lo, /"amount"[[:space:]]*:[[:space:]]*([0-9.]+)/, resultado)) {
                loamount = resultado[1];
                gsub(/\./, ",", loamount)
            } else {
                loamount = "";
            }
        } else {
            lo = "";
            loamount = "";
        }
    
        # latitude
        if (match(linea, /"latitude"[[:space:]]*:[[:space:]]*(-?[0-9.]+)/, resultado)) {
            lat = resultado[1];
            gsub(/\./, ",", lat)
        } else { lat = ""; }
    
        # longitude
        if (match(linea, /"longitude"[[:space:]]*:[[:space:]]*(-?[0-9.]+)/, resultado)) {
            long = resultado[1];
            gsub(/\./, ",", long)
        } else { long = ""; }

        # me quedo con las variables guardadas y voy a la siguiente linea, que debe ser la respuesta
        raw = linea
        gsub(/;/,"|",raw)
        next;
    }
    
    # ----- ahora leo la respuesta e imprimo
    if ( match(linea, /125 ==/ )) {
        result = substr(linea, RSTART + RLENGTH);
        split(result, tokens, " ");
        cod_resp  = tokens[2];
        respuesta = tokens[3];
        httpstatus = cod_resp " " respuesta;
        # imprimo en una linea todos los datos separados por ; para que funcione como archivo csv
        print "STi;" fechahora ";" tipo ";" numero ";" tiponum ";" metodo ";" host ";" host2 ";" api ";" apisola ";" ver ";" httpstatus ";" ts ";" soi ";" vn ";" stn ";" st ";" sts ";" lat ";" long ";" eta ";" amount ";" loamount ";" mess ";" raw;
    }

}
