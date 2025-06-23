// lib/core/network/network_setup.dart

import '../storage/storage_service.dart';
import 'http_client.dart';

/// Configuração centralizada da rede
/// 
/// Este arquivo é responsável por inicializar todos os serviços de rede
/// de forma ordenada e garantir que tudo esteja funcionando antes do app começar.
class NetworkSetup {
  
  /// Inicializa todos os serviços de rede
  /// 
  /// Este método deve ser chamado no main.dart antes de rodar o app
  static Future<void> initialize() async {
    print('🚀 Inicializando serviços de rede...');
    
    try {
      // 1. Inicializa o storage primeiro (é dependência do HttpClient)
      await StorageService.instance.init();
      print('✅ StorageService inicializado');
      
      // 2. HttpClient já é inicializado automaticamente no seu constructor
      // Mas podemos fazer um teste de conectividade opcional
      final httpClient = HttpClient.instance;
      print('✅ HttpClient configurado');
      
      // 3. Teste opcional de conectividade (não bloqueia se falhar)
      try {
        final isConnected = await httpClient.testConnection();
        if (isConnected) {
          print('✅ Conectividade com API confirmada');
        } else {
          print('⚠️  API indisponível, mas app pode funcionar offline');
        }
      } catch (e) {
        print('⚠️  Não foi possível testar conectividade: $e');
      }
      
      print('🎉 Todos os serviços de rede inicializados com sucesso!');
      
    } catch (e) {
      print('❌ Erro crítico na inicialização da rede: $e');
      rethrow; // Re-lança o erro para que seja tratado no main.dart
    }
  }
  
  /// Informações de debug sobre todos os serviços
  static Future<Map<String, dynamic>> getSystemInfo() async {
    try {
      final storageInfo = await StorageService.instance.getDebugInfo();
      final httpInfo = HttpClient.instance.getDebugInfo();
      
      return {
        'timestamp': DateTime.now().toIso8601String(),
        'storage': storageInfo,
        'http': httpInfo,
        'system': {
          'platform': 'Flutter',
          'version': '1.0.0',
        }
      };
    } catch (e) {
      return {
        'error': 'Falha ao coletar informações: $e',
        'timestamp': DateTime.now().toIso8601String(),
      };
    }
  }
  
  /// Reset completo do sistema (útil para logout ou debug)
  static Future<void> reset() async {
    print('🔄 Resetando sistema de rede...');
    
    try {
      // Limpa dados do storage
      await StorageService.instance.clearAll();
      
      // Reseta interceptors do HttpClient
      HttpClient.instance.clearInterceptors();
      
      print('✅ Sistema resetado com sucesso');
      
    } catch (e) {
      print('❌ Erro ao resetar sistema: $e');
      rethrow;
    }
  }
}