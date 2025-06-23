// lib/core/storage/storage_service.dart

import 'dart:convert';
import 'package:shared_preferences/shared_preferences.dart';
import '../constants/api_constants.dart';

/// Serviço de armazenamento local seguro
/// 
/// Este é o "cofre digital" do nosso app. Responsável por:
/// - Guardar token JWT de forma segura
/// - Armazenar dados do usuário localmente
/// - Gerenciar preferências do app
/// - Manter estado entre sessões
class StorageService {
  static StorageService? _instance;
  SharedPreferences? _prefs;
  
  // Singleton pattern - uma única instância do cofre para todo o app
  StorageService._();
  
  static StorageService get instance {
    _instance ??= StorageService._();
    return _instance!;
  }
  
  // ========================================================================
  // INICIALIZAÇÃO - "Abrindo o Cofre"
  // ========================================================================
  
  /// Inicializa o serviço de armazenamento
  /// Deve ser chamado antes de usar qualquer método
  Future<void> init() async {
    _prefs ??= await SharedPreferences.getInstance();
  }
  
  /// Garante que o serviço foi inicializado
  void _ensureInitialized() {
    if (_prefs == null) {
      throw Exception('StorageService não foi inicializado. Chame init() primeiro.');
    }
  }
  
  // ========================================================================
  // GERENCIAMENTO DE TOKEN JWT - "Crachá de Acesso"
  // ========================================================================
  
  /// Salva o token JWT recebido após login
  Future<bool> saveAccessToken(String token) async {
    _ensureInitialized();
    
    try {
      final success = await _prefs!.setString(ApiConstants.storageKeys.accessToken, token);
      
      if (success) {
        // Salva também o timestamp do login para controle de expiração
        await _prefs!.setInt(
          ApiConstants.storageKeys.lastLoginTime,
          DateTime.now().millisecondsSinceEpoch,
        );
      }
      
      return success;
    } catch (e) {
      print('Erro ao salvar token: $e');
      return false;
    }
  }
  
  /// Recupera o token JWT salvo
  Future<String?> getAccessToken() async {
    _ensureInitialized();
    
    try {
      return _prefs!.getString(ApiConstants.storageKeys.accessToken);
    } catch (e) {
      print('Erro ao recuperar token: $e');
      return null;
    }
  }
  
  /// Verifica se existe um token válido salvo
  Future<bool> hasValidToken() async {
    final token = await getAccessToken();
    
    if (token == null || token.isEmpty) {
      return false;
    }
    
    // TODO: Adicionar verificação de expiração do token no futuro
    // Por enquanto, considera válido se existe
    return true;
  }
  
  /// Remove o token (usado no logout)
  Future<bool> removeAccessToken() async {
    _ensureInitialized();
    
    try {
      final tokenRemoved = await _prefs!.remove(ApiConstants.storageKeys.accessToken);
      final timeRemoved = await _prefs!.remove(ApiConstants.storageKeys.lastLoginTime);
      
      return tokenRemoved && timeRemoved;
    } catch (e) {
      print('Erro ao remover token: $e');
      return false;
    }
  }
  
  // ========================================================================
  // DADOS DO USUÁRIO - "Carteira de Identidade Digital"
  // ========================================================================
  
  /// Salva dados do usuário logado
  Future<bool> saveUserData(Map<String, dynamic> userData) async {
    _ensureInitialized();
    
    try {
      final jsonString = jsonEncode(userData);
      return await _prefs!.setString(ApiConstants.storageKeys.userData, jsonString);
    } catch (e) {
      print('Erro ao salvar dados do usuário: $e');
      return false;
    }
  }
  
  /// Recupera dados do usuário logado
  Future<Map<String, dynamic>?> getUserData() async {
    _ensureInitialized();
    
    try {
      final jsonString = _prefs!.getString(ApiConstants.storageKeys.userData);
      
      if (jsonString == null) {
        return null;
      }
      
      return jsonDecode(jsonString) as Map<String, dynamic>;
    } catch (e) {
      print('Erro ao recuperar dados do usuário: $e');
      return null;
    }
  }
  
  /// Remove dados do usuário (usado no logout)
  Future<bool> removeUserData() async {
    _ensureInitialized();
    
    try {
      return await _prefs!.remove(ApiConstants.storageKeys.userData);
    } catch (e) {
      print('Erro ao remover dados do usuário: $e');
      return false;
    }
  }
  
  // ========================================================================
  // PREFERÊNCIAS DO APP - "Configurações Pessoais"
  // ========================================================================
  
  /// Verifica se é a primeira vez que o usuário abre o app
  Future<bool> isFirstTime() async {
    _ensureInitialized();
    
    return _prefs!.getBool(ApiConstants.storageKeys.isFirstTime) ?? true;
  }
  
  /// Marca que não é mais a primeira vez
  Future<void> setNotFirstTime() async {
    _ensureInitialized();
    
    await _prefs!.setBool(ApiConstants.storageKeys.isFirstTime, false);
  }
  
  /// Salva uma preferência genérica (string)
  Future<bool> savePreference(String key, String value) async {
    _ensureInitialized();
    
    try {
      return await _prefs!.setString(key, value);
    } catch (e) {
      print('Erro ao salvar preferência $key: $e');
      return false;
    }
  }
  
  /// Recupera uma preferência genérica (string)
  Future<String?> getPreference(String key) async {
    _ensureInitialized();
    
    try {
      return _prefs!.getString(key);
    } catch (e) {
      print('Erro ao recuperar preferência $key: $e');
      return null;
    }
  }
  
  /// Salva uma preferência booleana
  Future<bool> saveBoolPreference(String key, bool value) async {
    _ensureInitialized();
    
    try {
      return await _prefs!.setBool(key, value);
    } catch (e) {
      print('Erro ao salvar preferência booleana $key: $e');
      return false;
    }
  }
  
  /// Recupera uma preferência booleana
  Future<bool> getBoolPreference(String key, {bool defaultValue = false}) async {
    _ensureInitialized();
    
    try {
      return _prefs!.getBool(key) ?? defaultValue;
    } catch (e) {
      print('Erro ao recuperar preferência booleana $key: $e');
      return defaultValue;
    }
  }
  
  // ========================================================================
  // LIMPEZA GERAL - "Faxina do Cofre"
  // ========================================================================
  
  /// Remove todos os dados (usado em logout completo ou reset do app)
  Future<bool> clearAll() async {
    _ensureInitialized();
    
    try {
      return await _prefs!.clear();
    } catch (e) {
      print('Erro ao limpar todos os dados: $e');
      return false;
    }
  }
  
  /// Remove apenas dados de autenticação (mantém preferências)
  Future<bool> clearAuthData() async {
    _ensureInitialized();
    
    try {
      final tokenRemoved = await removeAccessToken();
      final userRemoved = await removeUserData();
      
      return tokenRemoved && userRemoved;
    } catch (e) {
      print('Erro ao limpar dados de autenticação: $e');
      return false;
    }
  }
  
  // ========================================================================
  // MÉTODOS DE DEBUG - "Inspeção do Cofre"
  // ========================================================================
  
  /// Lista todas as chaves armazenadas (útil para debug)
  Future<Set<String>> getAllKeys() async {
    _ensureInitialized();
    
    return _prefs!.getKeys();
  }
  
  /// Mostra informações de debug sobre o storage
  Future<Map<String, dynamic>> getDebugInfo() async {
    _ensureInitialized();
    
    final hasToken = await hasValidToken();
    final hasUser = await getUserData() != null;
    final isFirst = await isFirstTime();
    final keys = await getAllKeys();
    
    return {
      'hasValidToken': hasToken,
      'hasUserData': hasUser,
      'isFirstTime': isFirst,
      'totalKeys': keys.length,
      'allKeys': keys.toList(),
    };
  }
}

// ============================================================================
// EXTENSÕES ÚTEIS - "Ferramentas Extras"
// ============================================================================

/// Extensão para facilitar o uso do StorageService
extension StorageServiceExtension on StorageService {
  
  /// Método de conveniência para verificar se usuário está logado
  Future<bool> get isLoggedIn async {
    final hasToken = await hasValidToken();
    final hasUser = await getUserData() != null;
    
    return hasToken && hasUser;
  }
  
  /// Método de conveniência para logout completo
  Future<bool> logout() async {
    return await clearAuthData();
  }
}