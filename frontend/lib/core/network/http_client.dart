// lib/core/network/http_client.dart

import 'package:dio/dio.dart';
import '../constants/api_constants.dart';
import '../storage/storage_service.dart';

/// Cliente HTTP configurado para comunicação com nossa API
/// 
/// Este é o "departamento de comunicações" do nosso app. É responsável por:
/// - Adicionar automaticamente o token JWT em todas as requisições
/// - Tratar erros de forma consistente
/// - Fazer retry automático em caso de falhas temporárias
/// - Logar requisições para debugging
/// - Gerenciar timeouts e configurações de rede
class HttpClient {
  static HttpClient? _instance;
  late Dio _dio;
  final StorageService _storage = StorageService.instance;
  
  // Singleton pattern - um único "departamento de comunicações" para todo o app
  HttpClient._() {
    _setupDio();
  }
  
  static HttpClient get instance {
    _instance ??= HttpClient._();
    return _instance!;
  }
  
  /// Getter para acessar o Dio configurado
  Dio get dio => _dio;
  
  // ========================================================================
  // CONFIGURAÇÃO INICIAL - "Montando a Central Telefônica"
  // ========================================================================
  
  void _setupDio() {
    _dio = Dio(BaseOptions(
      baseUrl: ApiConstants.apiBaseUrl,
      connectTimeout: ApiConstants.connectTimeout,
      receiveTimeout: ApiConstants.receiveTimeout,
      sendTimeout: ApiConstants.sendTimeout,
      headers: ApiConstants.defaultHeaders,
      
      // Configurações importantes para debugging
      validateStatus: (status) {
        // Considera sucesso códigos 200-299
        // Códigos 400+ serão tratados como erro nos interceptors
        return status != null && status < 400;
      },
    ));
    
    // Configura os interceptors - é aqui que a "magia" acontece
    _setupInterceptors();
  }
  
  // ========================================================================
  // INTERCEPTORS - "Secretárias Eletrônicas Inteligentes"
  // ========================================================================
  
  void _setupInterceptors() {
    
    // ====== INTERCEPTOR DE AUTENTICAÇÃO ======
    // Adiciona automaticamente o token JWT em todas as requisições protegidas
    _dio.interceptors.add(InterceptorsWrapper(
      onRequest: (options, handler) async {
        await _addAuthToken(options);
        handler.next(options);
      },
    ));
    
    // ====== INTERCEPTOR DE LOGS ======
    // Registra todas as requisições para debugging (apenas em desenvolvimento)
    _dio.interceptors.add(LogInterceptor(
      requestBody: true,
      responseBody: true,
      requestHeader: true,
      responseHeader: false,
      error: true,
      logPrint: (object) {
        // Em produção, você pode desabilitar ou enviar para serviço de logs
        print('🌐 HTTP: $object');
      },
    ));
    
    // ====== INTERCEPTOR DE ERRO E RETRY ======
    // Trata erros comuns e faz retry automático quando apropriado
    _dio.interceptors.add(InterceptorsWrapper(
      onError: (error, handler) async {
        await _handleError(error, handler);
      },
    ));
  }
  
  // ========================================================================
  // GERENCIAMENTO DE AUTENTICAÇÃO - "Crachá Automático"
  // ========================================================================
  
  /// Adiciona token JWT automaticamente se disponível
  Future<void> _addAuthToken(RequestOptions options) async {
    try {
      // Busca token do storage
      final token = await _storage.getAccessToken();
      
      if (token != null && token.isNotEmpty) {
        // Adiciona header de autorização
        options.headers['Authorization'] = ApiConstants.authHeader(token);
        
        print('🔐 Token adicionado à requisição: ${options.path}');
      } else {
        print('⚠️  Nenhum token disponível para: ${options.path}');
      }
    } catch (e) {
      print('❌ Erro ao adicionar token: $e');
    }
  }
  
  // ========================================================================
  // TRATAMENTO DE ERROS - "Resolução de Problemas"
  // ========================================================================
  
  /// Trata erros de forma inteligente e faz retry quando apropriado
  Future<void> _handleError(DioException error, ErrorInterceptorHandler handler) async {
    print('🚨 Erro HTTP: ${error.type} - ${error.message}');
    
    // Tratamento específico para diferentes tipos de erro
    switch (error.type) {
      
      case DioExceptionType.connectionTimeout:
      case DioExceptionType.sendTimeout:
      case DioExceptionType.receiveTimeout:
        // Para timeouts, tenta novamente automaticamente
        if (_shouldRetry(error)) {
          await _retryRequest(error, handler);
          return;
        }
        break;
        
      case DioExceptionType.badResponse:
        final statusCode = error.response?.statusCode;
        
        if (statusCode == 401) {
          // Token expirado ou inválido - limpa dados de auth
          await _handleUnauthorized();
        } else if (statusCode != null && ApiConstants.shouldRetry(statusCode)) {
          // Erros de servidor - tenta novamente
          if (_shouldRetry(error)) {
            await _retryRequest(error, handler);
            return;
          }
        }
        break;
        
      case DioExceptionType.connectionError:
        // Problemas de rede - tenta novamente
        if (_shouldRetry(error)) {
          await _retryRequest(error, handler);
          return;
        }
        break;
        
      default:
        break;
    }
    
    // Se chegou até aqui, não vai fazer retry - passa o erro adiante
    handler.next(error);
  }
  
  /// Lida com erro 401 (não autorizado)
  Future<void> _handleUnauthorized() async {
    print('🚪 Sessão expirada - limpando dados de autenticação');
    
    try {
      await _storage.clearAuthData();
      
      // TODO: Navegar para tela de login
      // Isso será implementado quando tivermos o sistema de navegação
      
    } catch (e) {
      print('❌ Erro ao limpar dados de auth: $e');
    }
  }
  
  // ========================================================================
  // SISTEMA DE RETRY - "Persistência na Comunicação"
  // ========================================================================
  
  /// Verifica se deve tentar a requisição novamente
  bool _shouldRetry(DioException error) {
    // Recupera contador de tentativas (armazenado nas options da requisição)
    final retryCount = error.requestOptions.extra['retryCount'] as int? ?? 0;
    
    return retryCount < ApiConstants.maxRetries;
  }
  
  /// Executa retry da requisição com delay
  Future<void> _retryRequest(DioException error, ErrorInterceptorHandler handler) async {
    final retryCount = error.requestOptions.extra['retryCount'] as int? ?? 0;
    final newRetryCount = retryCount + 1;
    
    print('🔄 Tentativa $newRetryCount/${ApiConstants.maxRetries} para: ${error.requestOptions.path}');
    
    // Espera um tempo antes de tentar novamente
    await Future.delayed(ApiConstants.retryDelay);
    
    try {
      // Atualiza contador de tentativas
      error.requestOptions.extra['retryCount'] = newRetryCount;
      
      // Faz nova tentativa
      final response = await _dio.fetch(error.requestOptions);
      
      // Se chegou até aqui, a requisição foi bem-sucedida
      print('✅ Retry bem-sucedido na tentativa $newRetryCount');
      handler.resolve(response);
      
    } catch (e) {
      // Se falhou novamente, passa o erro original adiante
      print('❌ Retry $newRetryCount falhou: $e');
      handler.next(error);
    }
  }
  
  // ========================================================================
  // MÉTODOS DE CONVENIÊNCIA - "Atalhos Inteligentes"
  // ========================================================================
  
  /// GET com tratamento de erro
  Future<Response<T>> get<T>(
    String path, {
    Object? data,
    Map<String, dynamic>? queryParameters,
    Options? options,
    CancelToken? cancelToken,
    ProgressCallback? onReceiveProgress,
  }) async {
    try {
      return await _dio.get<T>(
        path,
        data: data,
        queryParameters: queryParameters,
        options: options,
        cancelToken: cancelToken,
        onReceiveProgress: onReceiveProgress,
      );
    } catch (e) {
      throw _createHttpException(e);
    }
  }
  
  /// POST com tratamento de erro
  Future<Response<T>> post<T>(
    String path, {
    Object? data,
    Map<String, dynamic>? queryParameters,
    Options? options,
    CancelToken? cancelToken,
    ProgressCallback? onSendProgress,
    ProgressCallback? onReceiveProgress,
  }) async {
    try {
      return await _dio.post<T>(
        path,
        data: data,
        queryParameters: queryParameters,
        options: options,
        cancelToken: cancelToken,
        onSendProgress: onSendProgress,
        onReceiveProgress: onReceiveProgress,
      );
    } catch (e) {
      throw _createHttpException(e);
    }
  }
  
  /// PUT com tratamento de erro
  Future<Response<T>> put<T>(
    String path, {
    Object? data,
    Map<String, dynamic>? queryParameters,
    Options? options,
    CancelToken? cancelToken,
    ProgressCallback? onSendProgress,
    ProgressCallback? onReceiveProgress,
  }) async {
    try {
      return await _dio.put<T>(
        path,
        data: data,
        queryParameters: queryParameters,
        options: options,
        cancelToken: cancelToken,
        onSendProgress: onSendProgress,
        onReceiveProgress: onReceiveProgress,
      );
    } catch (e) {
      throw _createHttpException(e);
    }
  }
  
  /// DELETE com tratamento de erro
  Future<Response<T>> delete<T>(
    String path, {
    Object? data,
    Map<String, dynamic>? queryParameters,
    Options? options,
    CancelToken? cancelToken,
  }) async {
    try {
      return await _dio.delete<T>(
        path,
        data: data,
        queryParameters: queryParameters,
        options: options,
        cancelToken: cancelToken,
      );
    } catch (e) {
      throw _createHttpException(e);
    }
  }
  
  // ========================================================================
  // TRATAMENTO DE EXCEÇÕES - "Tradutor de Problemas"
  // ========================================================================
  
  /// Converte exceções do Dio em exceções mais amigáveis
  HttpException _createHttpException(dynamic error) {
    if (error is DioException) {
      switch (error.type) {
        case DioExceptionType.connectionTimeout:
        case DioExceptionType.sendTimeout:
        case DioExceptionType.receiveTimeout:
          return HttpException(
            message: ApiConstants.errorMessages.timeoutError,
            statusCode: 408,
            originalError: error,
          );
          
        case DioExceptionType.connectionError:
          return HttpException(
            message: ApiConstants.errorMessages.networkError,
            statusCode: 0,
            originalError: error,
          );
          
        case DioExceptionType.badResponse:
          final statusCode = error.response?.statusCode ?? 0;
          final message = _extractErrorMessage(error.response) ?? 
                         ApiConstants.getErrorMessage(statusCode);
          
          return HttpException(
            message: message,
            statusCode: statusCode,
            originalError: error,
            response: error.response,
          );
          
        default:
          return HttpException(
            message: ApiConstants.errorMessages.unknownError,
            statusCode: 0,
            originalError: error,
          );
      }
    }
    
    return HttpException(
      message: ApiConstants.errorMessages.unknownError,
      statusCode: 0,
      originalError: error,
    );
  }
  
  /// Extrai mensagem de erro da resposta da API
  String? _extractErrorMessage(Response? response) {
    try {
      if (response?.data is Map<String, dynamic>) {
        final data = response!.data as Map<String, dynamic>;
        
        // Tenta diferentes campos onde a mensagem pode estar
        return data['message'] ?? 
               data['detail'] ?? 
               data['error'] ?? 
               data['msg'];
      }
    } catch (e) {
      print('❌ Erro ao extrair mensagem: $e');
    }
    
    return null;
  }
  
  // ========================================================================
  // MÉTODOS DE CONFIGURAÇÃO - "Ajustes da Central"
  // ========================================================================
  
  /// Atualiza token manualmente (útil após login)
  Future<void> updateToken(String token) async {
    await _storage.saveAccessToken(token);
    print('🔐 Token atualizado no HttpClient');
  }
  
  /// Remove token manualmente (útil no logout)
  Future<void> clearToken() async {
    await _storage.removeAccessToken();
    print('🚪 Token removido do HttpClient');
  }
  
  /// Configura URL base dinamicamente (útil para testes)
  void updateBaseUrl(String newBaseUrl) {
    _dio.options.baseUrl = newBaseUrl;
    print('🌐 Base URL atualizada para: $newBaseUrl');
  }
  
  /// Adiciona interceptor customizado
  void addInterceptor(Interceptor interceptor) {
    _dio.interceptors.add(interceptor);
    print('📡 Interceptor customizado adicionado');
  }
  
  /// Remove todos os interceptors (útil para testes)
  void clearInterceptors() {
    _dio.interceptors.clear();
    _setupInterceptors(); // Re-adiciona os interceptors padrão
    print('🧹 Interceptors resetados');
  }
  
  // ========================================================================
  // MÉTODOS DE DEBUG - "Inspeção da Central"
  // ========================================================================
  
  /// Informações de debug sobre o client
  Map<String, dynamic> getDebugInfo() {
    return {
      'baseUrl': _dio.options.baseUrl,
      'connectTimeout': _dio.options.connectTimeout?.inSeconds,
      'receiveTimeout': _dio.options.receiveTimeout?.inSeconds,
      'sendTimeout': _dio.options.sendTimeout?.inSeconds,
      'interceptorsCount': _dio.interceptors.length,
      'defaultHeaders': _dio.options.headers,
    };
  }
  
  /// Testa conectividade com a API
  Future<bool> testConnection() async {
    try {
      print('🔍 Testando conectividade com a API...');
      
      final response = await _dio.get('/health');
      
      print('✅ Conectividade OK: ${response.statusCode}');
      return true;
      
    } catch (e) {
      print('❌ Falha na conectividade: $e');
      return false;
    }
  }
}

// ============================================================================
// CLASSES DE EXCEÇÃO CUSTOMIZADAS - "Dicionário de Problemas"
// ============================================================================

/// Exceção HTTP customizada para erros mais informativos
class HttpException implements Exception {
  final String message;
  final int statusCode;
  final dynamic originalError;
  final Response? response;
  
  const HttpException({
    required this.message,
    required this.statusCode,
    this.originalError,
    this.response,
  });
  
  @override
  String toString() {
    return 'HttpException($statusCode): $message';
  }
  
  /// Verifica se é erro de rede
  bool get isNetworkError => statusCode == 0;
  
  /// Verifica se é erro de timeout
  bool get isTimeoutError => statusCode == 408;
  
  /// Verifica se é erro de autorização
  bool get isAuthError => statusCode == 401 || statusCode == 403;
  
  /// Verifica se é erro do servidor
  bool get isServerError => statusCode >= 500;
  
  /// Verifica se é erro de validação
  bool get isValidationError => statusCode == 400 || statusCode == 422;
}

// ============================================================================
// EXTENSÕES ÚTEIS - "Ferramentas Auxiliares"
// ============================================================================

/// Extensão para Response do Dio
extension ResponseExtension on Response {
  
  /// Verifica se a resposta foi bem-sucedida
  bool get isSuccess => statusCode != null && statusCode! >= 200 && statusCode! < 300;
  
  /// Extrai dados de forma segura
  T? safeData<T>() {
    try {
      return data as T;
    } catch (e) {
      print('❌ Erro ao extrair dados: $e');
      return null;
    }
  }
}