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
        // Sectores generales
        "General",
        "Industria manufacturera",
        "Servicios",
        "Comercio",
        "Tecnología",

        // Sectores específicos
        "Agroalimentario",
        "Agrícola",
        "Ganadero",
        "Forestal",
        "Pesca y acuicultura",

        "Construcción",
        "Inmobiliario",

        "Transporte y logística",
        "Automoción",

        "Energía",
        "Energías renovables",
        "Medio ambiente",
        "Economía circular",

        "TIC - Tecnologías de la Información",
        "Telecomunicaciones",
        "Software",
        "Ciberseguridad",
        "Inteligencia Artificial",

        "Biotecnología",
        "Farmacéutico",
        "Salud y sanidad",

        "Turismo",
        "Hostelería",
        "Cultura",
        "Ocio y entretenimiento",

        "Educación y formación",
        "Investigación científica",

        "Servicios financieros",
        "Seguros",

        "Comercio minorista",
        "Comercio electrónico",

        "Química",
        "Textil y confección",
        "Metalurgia",
        "Artesanía"
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
        // Fondos principales
        "FEDER - Fondo Europeo de Desarrollo Regional",
        "FSE+ - Fondo Social Europeo Plus",
        "FEADER - Fondo Europeo Agrícola de Desarrollo Rural",
        "FEMP - Fondo Europeo Marítimo, de Pesca y de Acuicultura",

        // Next Generation EU
        "Next Generation EU",
        "PRTR - Plan de Recuperación, Transformación y Resiliencia",
        "MRR - Mecanismo de Recuperación y Resiliencia",

        // Fondos específicos
        "Fondo de Transición Justa (FTJ)",
        "REACT-EU",

        // Programas europeos
        "Horizonte Europa",
        "LIFE",
        "CEF - Connecting Europe Facility",
        "InvestEU",

        // Sin fondos europeos
        "Sin fondos europeos específicos"
    ],

    tipo_ayuda: [
        "Subvención",
        "Préstamo",
        "Préstamo participativo",
        "Línea de crédito",
        "Garantía",
        "Aval",
        "Inversión en capital",
        "Venture capital",
        "Incentivo fiscal",
        "Deducción fiscal",
        "Bonificación",
        "Exención",
        "Servicios de asesoramiento",
        "Formación gratuita",
        "Ayuda en especie"
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
