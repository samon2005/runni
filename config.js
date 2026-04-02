/**
 * ============================================================
 * RUNNI - Configuración Central
 * ============================================================
 * 
 * Este archivo centraliza toda la configuración del sistema.
 * Cuando llegue la API de Runni, solo hay que modificar este archivo.
 * 
 * PENDIENTE DE RUNNI:
 * - URL base de la API
 * - API Key o método de autenticación
 * - Estructura de los endpoints
 * - Formato de los datos (posiciones, rutas, históricos)
 */

const RUNNI_CONFIG = {
    
    // ============================================================
    // API DE RUNNI (PENDIENTE - Completar cuando esté disponible)
    // ============================================================
    
    API: {
        // URL base de la API
        BASE_URL: null, // Ejemplo: 'https://api.runni.co/v1'
        
        // Autenticación
        API_KEY: null,
        AUTH_TYPE: 'Bearer', // 'Bearer', 'Basic', 'API-Key'
        
        // Endpoints (ajustar según documentación de Runni)
        ENDPOINTS: {
            // Posiciones en tiempo real
            POSICIONES: '/bikes/positions',
            
            // Histórico de rutas (últimos 3 meses)
            HISTORICO_RUTAS: '/bikes/history',
            
            // Información de bicicletas
            BICICLETAS: '/bikes',
            
            // Estaciones
            ESTACIONES: '/stations',
            
            // Domiciliarios
            DOMICILIARIOS: '/riders',
            
            // Estadísticas
            ESTADISTICAS: '/stats'
        },
        
        // Configuración de requests
        TIMEOUT: 10000, // ms
        RETRY_ATTEMPTS: 3,
        REFRESH_INTERVAL: 5000 // ms - cada cuánto actualizar posiciones
    },
    
    // ============================================================
    // DATOS ESPERADOS DE LA API
    // ============================================================
    
    // Estructura esperada de una bicicleta (ajustar según API real)
    BIKE_SCHEMA: {
        id: 'string',           // ID único de la bicicleta
        lat: 'number',          // Latitud actual
        lon: 'number',          // Longitud actual
        estado: 'string',       // 'en-ruta', 'disponible', 'en-espera', 'offline'
        bateria: 'number',      // Porcentaje de batería (si aplica)
        velocidad: 'number',    // km/h actual
        domiciliario_id: 'string',
        timestamp: 'ISO8601',   // Última actualización
        
        // Si está en ruta
        ruta_actual: {
            origen: { lat: 'number', lon: 'number', nombre: 'string' },
            destino: { lat: 'number', lon: 'number', nombre: 'string' },
            inicio: 'ISO8601',
            eta: 'ISO8601'
        }
    },
    
    // Estructura esperada del histórico
    HISTORY_SCHEMA: {
        bike_id: 'string',
        fecha: 'YYYY-MM-DD',
        rutas: [
            {
                inicio: 'ISO8601',
                fin: 'ISO8601',
                origen: { lat: 'number', lon: 'number' },
                destino: { lat: 'number', lon: 'number' },
                distancia_km: 'number',
                duracion_min: 'number',
                waypoints: [[/* lat, lon */]]
            }
        ]
    },
    
    // ============================================================
    // GEOGRAFÍA - Valle de Aburrá
    // ============================================================
    
    GEO: {
        // Límites del Valle de Aburrá
        BOUNDS: {
            NORTE: 6.40,
            SUR: 6.08,
            ESTE: -75.50,
            OESTE: -75.72
        },
        
        // Centros de referencia
        CENTROS: {
            MEDELLIN: [6.2442, -75.5812],
            BELLO: [6.3389, -75.5578],
            ENVIGADO: [6.1752, -75.5940],
            SABANETA: [6.1514, -75.6160],
            ITAGUI: [6.1849, -75.5990]
        },
        
        // Zoom por defecto
        DEFAULT_ZOOM: 13
    },
    
    // ============================================================
    // ESTACIONES ACTUALES DE RUNNI
    // ============================================================
    
    ESTACIONES: [
        {
            id: 'E01',
            nombre: 'Sede Socya Guayabal',
            tipo: 'sede_principal',
            lat: 6.2321,
            lon: -75.5815,
            capacidad: 50,
            servicios: ['contratos', 'mantenimiento', 'carga']
        },
        {
            id: 'E02',
            nombre: 'Estación Laureles',
            tipo: 'estacion',
            lat: 6.2441,
            lon: -75.5897,
            capacidad: 20,
            servicios: ['carga', 'descanso']
        },
        {
            id: 'E03',
            nombre: 'Estación Olaya Herrera',
            tipo: 'estacion',
            lat: 6.2138,
            lon: -75.5852,
            capacidad: 15,
            servicios: ['carga']
        }
    ],
    
    // ============================================================
    // DATOS DE PRUEBA (Borrador - Eliminar cuando llegue la API)
    // ============================================================
    
    DEMO_MODE: true, // Cambiar a false cuando la API esté lista
    
    // Restaurantes de prueba (orígenes de pedidos)
    DEMO_RESTAURANTES: [
        { id: 'R01', nombre: 'Crepes & Waffles Poblado', lat: 6.2086, lon: -75.5680, zona: 'El Poblado' },
        { id: 'R02', nombre: 'Mondongos El Poblado', lat: 6.2095, lon: -75.5665, zona: 'El Poblado' },
        { id: 'R03', nombre: 'Hacienda Junin', lat: 6.2518, lon: -75.5636, zona: 'Centro' },
        { id: 'R04', nombre: 'Burger King Laureles', lat: 6.2450, lon: -75.5890, zona: 'Laureles' },
        { id: 'R05', nombre: 'El Corral Envigado', lat: 6.1752, lon: -75.5940, zona: 'Envigado' },
        { id: 'R06', nombre: 'Frisby Sabaneta', lat: 6.1514, lon: -75.6160, zona: 'Sabaneta' },
        { id: 'R07', nombre: 'Sandwich Qbano Estadio', lat: 6.2567, lon: -75.5894, zona: 'Estadio' },
        { id: 'R08', nombre: 'Archies Oviedo', lat: 6.2000, lon: -75.5750, zona: 'El Poblado' },
        { id: 'R09', nombre: 'Presto Bello', lat: 6.3389, lon: -75.5578, zona: 'Bello' },
        { id: 'R10', nombre: 'McDonalds Puerta Norte', lat: 6.3318, lon: -75.5472, zona: 'Bello' }
    ],
    
    // Zonas residenciales de prueba (destinos de domicilios)
    DEMO_ZONAS_RESIDENCIALES: [
        { id: 'ZR01', nombre: 'Manila / El Poblado', lat: 6.2050, lon: -75.5620, densidad: 'alta' },
        { id: 'ZR02', nombre: 'Astorga / El Poblado', lat: 6.1980, lon: -75.5700, densidad: 'alta' },
        { id: 'ZR03', nombre: 'Laureles Primer Parque', lat: 6.2460, lon: -75.5950, densidad: 'media' },
        { id: 'ZR04', nombre: 'Envigado Zona Rosa', lat: 6.1720, lon: -75.5900, densidad: 'alta' },
        { id: 'ZR05', nombre: 'Sabaneta Centro', lat: 6.1500, lon: -75.6140, densidad: 'media' },
        { id: 'ZR06', nombre: 'Belen La Palma', lat: 6.2300, lon: -75.6050, densidad: 'media' },
        { id: 'ZR07', nombre: 'Conquistadores', lat: 6.2520, lon: -75.5800, densidad: 'media' },
        { id: 'ZR08', nombre: 'Boston', lat: 6.2580, lon: -75.5600, densidad: 'baja' }
    ]
};

// ============================================================
// FUNCIONES AUXILIARES PARA LA API
// ============================================================

/**
 * Cliente para la API de Runni
 * Usar cuando la API esté disponible
 */
const RunniAPI = {
    
    /**
     * Hacer request a la API
     */
    async fetch(endpoint, options = {}) {
        if (RUNNI_CONFIG.DEMO_MODE) {
            console.warn('DEMO MODE: Usando datos simulados');
            return this.getDemoData(endpoint);
        }
        
        const url = `${RUNNI_CONFIG.API.BASE_URL}${endpoint}`;
        const headers = {
            'Content-Type': 'application/json'
        };
        
        // Agregar autenticación
        if (RUNNI_CONFIG.API.API_KEY) {
            if (RUNNI_CONFIG.API.AUTH_TYPE === 'Bearer') {
                headers['Authorization'] = `Bearer ${RUNNI_CONFIG.API.API_KEY}`;
            } else if (RUNNI_CONFIG.API.AUTH_TYPE === 'API-Key') {
                headers['X-API-Key'] = RUNNI_CONFIG.API.API_KEY;
            }
        }
        
        try {
            const response = await fetch(url, {
                ...options,
                headers: { ...headers, ...options.headers },
                timeout: RUNNI_CONFIG.API.TIMEOUT
            });
            
            if (!response.ok) {
                throw new Error(`API Error: ${response.status}`);
            }
            
            return await response.json();
            
        } catch (error) {
            console.error('Error en API Runni:', error);
            throw error;
        }
    },
    
    /**
     * Obtener posiciones actuales de todas las bicicletas
     */
    async getPosiciones() {
        return this.fetch(RUNNI_CONFIG.API.ENDPOINTS.POSICIONES);
    },
    
    /**
     * Obtener histórico de rutas
     * @param {string} fechaInicio - YYYY-MM-DD
     * @param {string} fechaFin - YYYY-MM-DD
     */
    async getHistorico(fechaInicio, fechaFin) {
        return this.fetch(
            `${RUNNI_CONFIG.API.ENDPOINTS.HISTORICO_RUTAS}?desde=${fechaInicio}&hasta=${fechaFin}`
        );
    },
    
    /**
     * Obtener estadísticas
     */
    async getEstadisticas() {
        return this.fetch(RUNNI_CONFIG.API.ENDPOINTS.ESTADISTICAS);
    },
    
    /**
     * Datos de demo (mientras no hay API)
     */
    getDemoData(endpoint) {
        // Simular delay de red
        return new Promise(resolve => {
            setTimeout(() => {
                if (endpoint.includes('positions')) {
                    resolve(this.generarBicicletasDemo());
                } else if (endpoint.includes('history')) {
                    resolve(this.generarHistoricoDemo());
                } else {
                    resolve([]);
                }
            }, 300);
        });
    },
    
    generarBicicletasDemo() {
        const estados = ['en-ruta', 'disponible', 'en-espera'];
        const bicicletas = [];
        
        for (let i = 1; i <= 25; i++) {
            const estado = estados[Math.floor(Math.random() * estados.length)];
            const restaurante = RUNNI_CONFIG.DEMO_RESTAURANTES[
                Math.floor(Math.random() * RUNNI_CONFIG.DEMO_RESTAURANTES.length)
            ];
            const destino = RUNNI_CONFIG.DEMO_ZONAS_RESIDENCIALES[
                Math.floor(Math.random() * RUNNI_CONFIG.DEMO_ZONAS_RESIDENCIALES.length)
            ];
            const estacion = RUNNI_CONFIG.ESTACIONES[
                Math.floor(Math.random() * RUNNI_CONFIG.ESTACIONES.length)
            ];
            
            let lat, lon;
            
            if (estado === 'en-ruta') {
                const progreso = Math.random();
                lat = restaurante.lat + (destino.lat - restaurante.lat) * progreso;
                lon = restaurante.lon + (destino.lon - restaurante.lon) * progreso;
            } else if (estado === 'disponible') {
                lat = restaurante.lat + (Math.random() - 0.5) * 0.002;
                lon = restaurante.lon + (Math.random() - 0.5) * 0.002;
            } else {
                lat = estacion.lat + (Math.random() - 0.5) * 0.001;
                lon = estacion.lon + (Math.random() - 0.5) * 0.001;
            }
            
            bicicletas.push({
                id: `RUNNI-${String(i).padStart(3, '0')}`,
                lat, lon, estado,
                bateria: Math.floor(Math.random() * 60) + 40,
                velocidad: estado === 'en-ruta' ? Math.floor(Math.random() * 15) + 10 : 0,
                domiciliario: `Domiciliario ${i}`,
                restaurante: estado !== 'en-espera' ? restaurante : null,
                destino: estado === 'en-ruta' ? destino : null,
                estacion,
                timestamp: new Date().toISOString(),
                domiciliosHoy: Math.floor(Math.random() * 12),
                distanciaHoy: Math.floor(Math.random() * 25) + 5
            });
        }
        
        return bicicletas;
    },
    
    generarHistoricoDemo() {
        // Placeholder para datos históricos
        return {
            mensaje: 'Histórico de 3 meses - Pendiente datos reales de Runni',
            periodo: {
                desde: '2024-01-01',
                hasta: '2024-03-31'
            },
            resumen: {
                total_rutas: 15000,
                total_km: 45000,
                promedio_diario: 500
            }
        };
    }
};

// Exportar para uso en otros archivos
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { RUNNI_CONFIG, RunniAPI };
}
