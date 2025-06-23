// lib/core/constants/api_constants.dart

/// Constantes centralizadas para comunicação com a API
/// 
/// Este arquivo é como o "catálogo telefônico" do nosso app.
/// Todas as URLs, timeouts e configurações de rede ficam aqui,
/// facilitando mudanças futuras e organização.
class ApiConstants {
  
  // ========================================================================
  // CONFIGURAÇÕES BASE - "Endereço da Central"
  // ========================================================================
  
  /// URL base da API em desenvolvimento
  /// Durante desenvolvimento, nossa API FastAPI roda em localhost:8000
  static const String baseUrl = 'http://localhost:8000';
  
  /// URL base para produção (será configurada no futuro)
  static const String productionBaseUrl = 'https://api.baby-tracker.app';
  
  /// Determina se estamos em modo debug para usar localhost
  static String get apiBaseUrl {
    // Em modo debug (desenvolvimento), usa localhost
    // Em release (produção), usa URL de produção
    const bool isDebug = bool.fromEnvironment('dart.vm.product') == false;
    return isDebug ? baseUrl : productionBaseUrl;
  }
  
  // ========================================================================
  // ENDPOINTS DE AUTENTICAÇÃO - "Departamento de Credenciais"
  // ========================================================================
  
  /// Endpoints relacionados à autenticação
  /// Baseados exatamente nos endpoints que criamos no FastAPI
  static const auth = AuthEndpoints();
  
  // ========================================================================
  // ENDPOINTS FUTUROS - "Departamentos em Expansão"
  // ========================================================================
  
  /// Endpoints para funcionalidades de amamentação (futuro)
  static const feeding = FeedingEndpoints();
  
  /// Endpoints para funcionalidades de sono (futuro)
  static const sleep = SleepEndpoints();
  
  /// Endpoints para upload de fotos (futuro)
  static const photos = PhotosEndpoints();
  
  // ========================================================================
  // CONFIGURAÇÕES DE TIMEOUT - "Paciência da Comunicação"
  // ========================================================================
  
  /// Timeout para conexão inicial
  /// Quanto tempo esperar para estabelecer conexão com o servidor
  static const Duration connectTimeout = Duration(seconds: 10);
  
  /// Timeout para receber resposta
  /// Quanto tempo esperar pela resposta após enviar requisição
  static const Duration receiveTimeout = Duration(seconds: 15);
  
  /// Timeout para enviar dados
  /// Quanto tempo esperar para enviar dados (importante para upload de fotos)
  static const Duration sendTimeout = Duration(seconds: 30);
  
  // ========================================================================
  // CONFIGURAÇÕES DE HEADERS - "Etiqueta de Comunicação"
  // ========================================================================
  
  /// Headers padrão para todas as requisições
  static const Map<String, String> defaultHeaders = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'User-Agent': 'BabyTracker-Flutter/1.0.0',
  };
  
  /// Header de autorização (será adicionado dinamicamente)
  static String authHeader(String token) => 'Bearer $token';
  
  // ========================================================================
  // CONFIGURAÇÕES DE RETRY - "Persistência na Comunicação"
  // ========================================================================
  
  /// Quantas vezes tentar novamente em caso de falha
  static const int maxRetries = 3;
  
  /// Delay entre tentativas
  static const Duration retryDelay = Duration(seconds: 2);
  
  /// Códigos de status que devem ser retentados
  static const List<int> retryStatusCodes = [408, 429, 500, 502, 503, 504];
  
  // ========================================================================
  // CONFIGURAÇÕES DE CACHE - "Memória da Comunicação"
  // ========================================================================
  
  /// Tempo de vida do cache para dados do usuário
  static const Duration userCacheDuration = Duration(minutes: 30);
  
  /// Tempo de vida do cache para listas
  static const Duration listCacheDuration = Duration(minutes: 5);
  
  // ========================================================================
  // REFERÊNCIAS ÀS CLASSES UTILITÁRIAS - "Atalhos Organizados"
  // ========================================================================
  
  /// Chaves para SharedPreferences
  static const storageKeys = StorageKeys();
  
  /// Mensagens amigáveis para erros comuns
  static const errorMessages = ErrorMessages();
  
  // ========================================================================
  // MÉTODOS UTILITÁRIOS - "Ferramentas Auxiliares"
  // ========================================================================
  
  /// Constrói URL completa para um endpoint
  static String buildUrl(String endpoint) {
    return '$apiBaseUrl$endpoint';
  }
  
  /// Verifica se é erro de rede que deve ser retentado
  static bool shouldRetry(int? statusCode) {
    return statusCode != null && retryStatusCodes.contains(statusCode);
  }
  
  /// Converte código de status em mensagem amigável
  static String getErrorMessage(int statusCode) {
    switch (statusCode) {
      case 400:
        return errorMessages.validationError;
      case 401:
        return errorMessages.unauthorizedError;
      case 403:
        return errorMessages.forbiddenError;
      case 404:
        return errorMessages.notFoundError;
      case 408:
        return errorMessages.timeoutError;
      case 500:
      case 502:
      case 503:
      case 504:
        return errorMessages.serverError;
      default:
        return errorMessages.unknownError;
    }
  }
}

// ============================================================================
// CLASSES DE ENDPOINTS SEPARADAS - "Departamentos Independentes"
// ============================================================================

/// Endpoints de autenticação
class AuthEndpoints {
  const AuthEndpoints();
  
  static const String base = '/api/v1/auth';
  
  /// POST /api/v1/auth/register - Cadastrar novo usuário
  String get register => '$base/register';
  
  /// POST /api/v1/auth/login - Fazer login
  String get login => '$base/login';
  
  /// GET /api/v1/auth/me - Dados do usuário atual
  String get me => '$base/me';
  
  /// PUT /api/v1/auth/me - Atualizar perfil
  String get updateProfile => '$base/me';
  
  /// POST /api/v1/auth/change-password - Alterar senha
  String get changePassword => '$base/change-password';
  
  /// POST /api/v1/auth/logout - Fazer logout
  String get logout => '$base/logout';
  
  /// GET /api/v1/auth/health - Health check auth
  String get health => '$base/health';
}

/// Endpoints de amamentação (futuro)
class FeedingEndpoints {
  const FeedingEndpoints();
  
  static const String base = '/api/v1/feeding';
  
  String get list => '$base/';
  String get create => '$base/';
  String detail(int id) => '$base/$id';
}

/// Endpoints de sono (futuro)
class SleepEndpoints {
  const SleepEndpoints();
  
  static const String base = '/api/v1/sleep';
  
  String get list => '$base/';
  String get create => '$base/';
  String detail(int id) => '$base/$id';
}

/// Endpoints de fotos (futuro)
class PhotosEndpoints {
  const PhotosEndpoints();
  
  static const String base = '/api/v1/photos';
  
  String get upload => '$base/upload';
  String get list => '$base/';
  String detail(int id) => '$base/$id';
}

// ============================================================================
// CLASSES UTILITÁRIAS - "Ferramentas de Apoio"
// ============================================================================

/// Chaves para SharedPreferences
class StorageKeys {
  const StorageKeys();
  
  /// Token JWT do usuário
  String get accessToken => 'access_token';
  
  /// Dados do usuário logado
  String get userData => 'user_data';
  
  /// Timestamp do último login
  String get lastLoginTime => 'last_login_time';
  
  /// Configurações do usuário
  String get userPreferences => 'user_preferences';
  
  /// Flag se é primeiro acesso
  String get isFirstTime => 'is_first_time';
}

/// Mensagens amigáveis para erros comuns
class ErrorMessages {
  const ErrorMessages();
  
  String get networkError => 'Erro de conexão. Verifique sua internet.';
  String get serverError => 'Erro no servidor. Tente novamente mais tarde.';
  String get timeoutError => 'Tempo limite excedido. Tente novamente.';
  String get unauthorizedError => 'Sessão expirada. Faça login novamente.';
  String get forbiddenError => 'Acesso negado.';
  String get notFoundError => 'Recurso não encontrado.';
  String get validationError => 'Dados inválidos. Verifique os campos.';
  String get unknownError => 'Erro inesperado. Tente novamente.';
}