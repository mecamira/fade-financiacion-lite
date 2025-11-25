// Opciones predefinidas para campos de clasificación
// Estas listas se usan para autocompletado en el formulario de edición manual

const OPCIONES_PREDEFINIDAS = {
    organismo: [
        // Organismos estatales principales
        "CDTI - Centro para el Desarrollo Tecnológico y la Innovación",
        "ENISA",
        "Red.es",
        "ICO - Instituto de Crédito Oficial",
        "ICEX - Instituto Español de Comercio Exterior",
        "Agencia Estatal de Investigación (AEI)",
        "IDAE - Instituto para la Diversificación y Ahorro de la Energía",
        "SEPE - Servicio Público de Empleo Estatal",
        "EOI - Escuela de Organización Industrial",

        // Ministerios
        "Ministerio de Ciencia, Innovación y Universidades",
        "Ministerio de Industria y Turismo",
        "Ministerio de Economía, Comercio y Empresa",
        "Ministerio de Cultura",
        "Ministerio de Agricultura, Pesca y Alimentación",
        "Ministerio de Defensa",

        // Principado de Asturias - Consejerías
        "Consejería de Ciencia, Empresas, Formación y Empleo",
        "Consejería de Transición Ecológica, Industria y Comercio",
        "Consejería de Medio Rural y Política Agraria",
        "Consejería de Cultura, Política Llingüística y Deporte",
        "Consejería de Presidencia, Reto Demográfico, Igualdad y Turismo",

        // Agencias autonómicas
        "SEKUENS - Agencia de Ciencia, Competitividad Empresarial e Innovación Asturiana",
        "SEPEPA - Servicio Público de Empleo del Principado de Asturias",
        "Sociedad Regional de Promoción del Principado de Asturias",

        // SGR y financiación
        "Asturgar S.G.R.",
        "MicroBank",

        // Cámaras de Comercio
        "Cámara de Comercio de Oviedo",
        "Cámara de Comercio de Gijón",
        "Cámara de Comercio de Avilés",

        // Ayuntamientos principales
        "Ayuntamiento de Oviedo",
        "Ayuntamiento de Gijón",
        "Ayuntamiento de Avilés"
    ],

    beneficiarios: [
        // Tipos de empresa por tamaño
        "Microempresas",
        "Pequeñas empresas",
        "Medianas empresas",
        "Grandes empresas",
        "PYMES",
        "Startups",

        // Tipos específicos
        "Autónomos",
        "Empresarios individuales",
        "Sociedades mercantiles",
        "Sociedades cooperativas",
        "Sociedades laborales",
        "Centros tecnológicos",
        "Empresas de Base Tecnológica (EBT)",

        // Sector público
        "Universidades públicas",
        "Universidades privadas",
        "Organismos públicos de investigación",
        "Entidades locales",
        "Ayuntamientos",

        // Sin ánimo de lucro
        "Entidades sin ánimo de lucro",
        "Asociaciones",
        "Fundaciones",
        "ONGs",
        "Cooperativas agrarias",

        // Sectores específicos
        "Empresas agrarias",
        "Empresas agroalimentarias",
        "Empresas forestales",
        "Empresas de economía social",
        "Centros de investigación",
        "Entidades sanitarias",

        // Individuos
        "Personas físicas",
        "Jóvenes emprendedores",
        "Mujeres emprendedoras",
        "Personas con discapacidad"
    ],

    sectores: [
        // Códigos CNAE oficiales de la BDNS
        "01 - Agricultura, ganadería, caza y servicios relacionados con las mismas",
        "02 - Silvicultura y explotación forestal",
        "03 - Pesca y acuicultura",
        "05 - Extracción de antracita, hulla y lignito",
        "06 - Extracción de crudo de petróleo y gas natural",
        "07 - Extracción de minerales metálicos",
        "08 - Otras industrias extractivas",
        "09 - Actividades de apoyo a las industrias extractivas",
        "10 - Industria de la alimentación",
        "11 - Fabricación de bebidas",
        "12 - Industria del tabaco",
        "13 - Industria textil",
        "14 - Confección de prendas de vestir",
        "15 - Industria del cuero y del calzado",
        "16 - Industria de la madera y del corcho, excepto muebles; cestería y espartería",
        "17 - Industria del papel",
        "18 - Artes gráficas y reproducción de soportes grabados",
        "19 - Coquerías y refino de petróleo",
        "20 - Industria química",
        "21 - Fabricación de productos farmacéuticos",
        "22 - Fabricación de productos de caucho y plásticos",
        "23 - Fabricación de otros productos minerales no metálicos",
        "24 - Metalurgia; fabricación de productos de hierro, acero y ferroaleaciones",
        "25 - Fabricación de productos metálicos, excepto maquinaria y equipo",
        "26 - Fabricación de productos informáticos, electrónicos y ópticos",
        "27 - Fabricación de material y equipo eléctrico",
        "28 - Fabricación de maquinaria y equipo n.c.o.p.",
        "29 - Fabricación de vehículos de motor, remolques y semirremolques",
        "30 - Fabricación de otro material de transporte",
        "31 - Fabricación de muebles",
        "32 - Otras industrias manufactureras",
        "33 - Reparación e instalación de maquinaria y equipo",
        "35 - Suministro de energía eléctrica, gas, vapor y aire acondicionado",
        "36 - Captación, depuración y distribución de agua",
        "37 - Recogida y tratamiento de aguas residuales",
        "38 - Recogida, tratamiento y eliminación de residuos; valorización",
        "39 - Actividades de descontaminación y otros servicios de gestión de residuos",
        "41 - Construcción de edificios",
        "42 - Ingeniería civil",
        "43 - Actividades de construcción especializada",
        "45 - Venta y reparación de vehículos de motor y motocicletas",
        "46 - Comercio al por mayor e intermediarios del comercio, excepto de vehículos de motor y motocicletas",
        "47 - Comercio al por menor, excepto de vehículos de motor y motocicletas",
        "49 - Transporte terrestre y por tubería",
        "50 - Transporte marítimo y por vías navegables interiores",
        "51 - Transporte aéreo",
        "52 - Almacenamiento y actividades anexas al transporte",
        "53 - Actividades postales y de correos",
        "55 - Servicios de alojamiento",
        "56 - Servicios de comidas y bebidas",
        "58 - Edición",
        "59 - Actividades cinematográficas, de vídeo y de programas de televisión, grabación de sonido y edición musical",
        "60 - Actividades de programación y emisión de radio y televisión",
        "61 - Telecomunicaciones",
        "62 - Programación, consultoría y otras actividades relacionadas con la informática",
        "63 - Servicios de información",
        "64 - Servicios financieros, excepto seguros y fondos de pensiones",
        "65 - Seguros, reaseguros y fondos de pensiones, excepto Seguridad Social obligatoria",
        "66 - Actividades auxiliares a los servicios financieros y a los seguros",
        "68 - Actividades inmobiliarias",
        "69 - Actividades jurídicas y de contabilidad",
        "70 - Actividades de las sedes centrales; actividades de consultoría de gestión empresarial",
        "71 - Servicios técnicos de arquitectura e ingeniería; ensayos y análisis técnicos",
        "72 - Investigación y desarrollo",
        "73 - Publicidad y estudios de mercado",
        "74 - Otras actividades profesionales, científicas y técnicas",
        "75 - Actividades veterinarias",
        "77 - Actividades de alquiler",
        "78 - Actividades relacionadas con el empleo",
        "79 - Actividades de agencias de viajes, operadores turísticos, servicios de reservas y actividades relacionadas con los mismos",
        "80 - Actividades de seguridad e investigación",
        "81 - Servicios a edificios y actividades de jardinería",
        "82 - Actividades administrativas de oficina y otras actividades auxiliares a las empresas",
        "84 - Administración Pública y defensa; Seguridad Social obligatoria",
        "85 - Educación",
        "86 - Actividades sanitarias",
        "87 - Asistencia en establecimientos residenciales",
        "88 - Actividades de servicios sociales sin alojamiento",
        "90 - Actividades de creación, artísticas y espectáculos",
        "91 - Actividades de bibliotecas, archivos, museos y otras actividades culturales",
        "92 - Actividades de juegos de azar y apuestas",
        "93 - Actividades deportivas, recreativas y de entretenimiento",
        "94 - Actividades asociativas",
        "95 - Reparación de ordenadores, efectos personales y artículos de uso doméstico",
        "96 - Otros servicios personales",
        "97 - Actividades de los hogares como empleadores de personal doméstico",
        "98 - Actividades de los hogares como productores de bienes y servicios para uso propio",
        "99 - Actividades de organizaciones y organismos extraterritoriales"
    ],

    tipo_proyecto: [
        // I+D+i
        "I+D+i",
        "Investigación industrial",
        "Desarrollo experimental",
        "Innovación tecnológica",
        "Innovación no tecnológica",

        // Digitalización
        "Digitalización",
        "Transformación digital",
        "Adopción soluciones digitales",
        "Industria 4.0",
        "Ciberseguridad",

        // Inversión
        "Inversión productiva",
        "Inversión en activos fijos",
        "Modernización de instalaciones",
        "Ampliación de capacidad",

        // Sostenibilidad
        "Sostenibilidad ambiental",
        "Eficiencia energética",
        "Energías renovables",
        "Economía circular",
        "Reducción de emisiones",

        // Formación y empleo
        "Formación profesional",
        "Capacitación",
        "Creación de empleo",

        // Comercialización
        "Internacionalización",
        "Exportación",
        "Marketing y comercialización",

        // Otros
        "Creación de empresas",
        "Cooperación empresarial",
        "Transferencia tecnológica",
        "Diversificación de actividades"
    ],

    fondos_europeos: [
        // Sin financiación
        "NO - Sin financiación europea",

        // Fondos principales
        "FEDER - Fondo Europeo de Desarrollo Regional",
        "FSE+ - Fondo Social Europeo Plus",
        "FEADER - Fondo Europeo Agrícola de Desarrollo Rural",
        "FEMPA - Fondo Europeo Marítimo, de Pesca y de Acuicultura",
        "FEAGA - Fondo Europeo Agrícola de Garantía",

        // Next Generation EU
        "MRR - Mecanismo de Recuperación y Resiliencia",
        "PRTR - Plan de Recuperación, Transformación y Resiliencia",
        "REACT-EU - Ayuda a la Recuperación para la Cohesión y los Territorios de Europa",
        "FTJ - Fondo de Transición Justa",

        // Programas europeos
        "HORIZON - Horizonte Europa",
        "LIFE - Programa LIFE",
        "CEF - Connecting Europe Facility",
        "INVESTEU - InvestEU"
    ],

    tipo_ayuda: [
        "Subvención",
        "Préstamo",
        "Garantía",
        "Aval",
        "Bonificación"
    ],

    tipo_convocatoria: [
        "Concurrencia Competitiva",
        "Concurrencia No Competitiva",
        "Concesión Directa"
    ]
};

// Función para obtener opciones de un campo
function getOpciones(campo) {
    return OPCIONES_PREDEFINIDAS[campo] || [];
}

// Exportar para uso en otros módulos
if (typeof module !== 'undefined' && module.exports) {
    module.exports = OPCIONES_PREDEFINIDAS;
}
