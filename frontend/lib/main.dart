// lib/main.dart

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

// Importar nossos serviços de rede
import 'core/network/network_setup.dart';

void main() async {
  // Garante que os widgets do Flutter estejam inicializados
  WidgetsFlutterBinding.ensureInitialized();
  
  print('🍼 Iniciando Baby Tracker...');
  
  try {
    // Inicializa todos os serviços de rede ANTES de rodar o app
    await NetworkSetup.initialize();
    
    // Roda o app com Riverpod (gerenciamento de estado)
    runApp(
      ProviderScope(
        child: MyApp(),
      ),
    );
    
  } catch (e) {
    print('❌ Erro crítico na inicialização: $e');
    
    // Em caso de erro crítico, ainda roda o app mas com estado de erro
    runApp(
      ProviderScope(
        child: ErrorApp(error: e.toString()),
      ),
    );
  }
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Baby Tracker',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.deepPurple),
        useMaterial3: true,
      ),
      home: const MyHomePage(title: 'Baby Tracker - Sistema de Comunicação Configurado!'),
    );
  }
}

class MyHomePage extends StatefulWidget {
  const MyHomePage({super.key, required this.title});

  final String title;

  @override
  State<MyHomePage> createState() => _MyHomePageState();
}

class _MyHomePageState extends State<MyHomePage> {
  Map<String, dynamic>? _systemInfo;
  bool _isLoading = false;

  @override
  void initState() {
    super.initState();
    _loadSystemInfo();
  }

  Future<void> _loadSystemInfo() async {
    setState(() => _isLoading = true);
    
    try {
      final info = await NetworkSetup.getSystemInfo();
      setState(() => _systemInfo = info);
    } catch (e) {
      print('Erro ao carregar info do sistema: $e');
    } finally {
      setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        backgroundColor: Theme.of(context).colorScheme.inversePrimary,
        title: Text(widget.title),
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            
            // Status da inicialização
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Icon(Icons.check_circle, color: Colors.green),
                        SizedBox(width: 8),
                        Text(
                          'Sistema de Comunicação Inicializado',
                          style: Theme.of(context).textTheme.titleMedium?.copyWith(
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ],
                    ),
                    SizedBox(height: 8),
                    Text('✅ StorageService configurado'),
                    Text('✅ HttpClient com interceptors automáticos'),
                    Text('✅ Gerenciamento de token JWT'),
                    Text('✅ Sistema de retry e error handling'),
                  ],
                ),
              ),
            ),
            
            SizedBox(height: 16),
            
            // Informações do sistema
            Text(
              'Informações do Sistema',
              style: Theme.of(context).textTheme.titleLarge,
            ),
            
            SizedBox(height: 8),
            
            if (_isLoading)
              Center(child: CircularProgressIndicator())
            else if (_systemInfo != null)
              Expanded(
                child: Card(
                  child: Padding(
                    padding: const EdgeInsets.all(16.0),
                    child: SingleChildScrollView(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          _buildInfoSection('Storage', _systemInfo!['storage']),
                          SizedBox(height: 16),
                          _buildInfoSection('HTTP Client', _systemInfo!['http']),
                          SizedBox(height: 16),
                          _buildInfoSection('Sistema', _systemInfo!['system']),
                        ],
                      ),
                    ),
                  ),
                ),
              ),
            
            SizedBox(height: 16),
            
            // Botões de ação
            Row(
              children: [
                Expanded(
                  child: ElevatedButton.icon(
                    onPressed: _loadSystemInfo,
                    icon: Icon(Icons.refresh),
                    label: Text('Recarregar Info'),
                  ),
                ),
                SizedBox(width: 8),
                Expanded(
                  child: ElevatedButton.icon(
                    onPressed: () {
                      ScaffoldMessenger.of(context).showSnackBar(
                        SnackBar(content: Text('Tela de login será implementada na próxima etapa!')),
                      );
                    },
                    icon: Icon(Icons.login),
                    label: Text('Ir para Login'),
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildInfoSection(String title, dynamic data) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          title,
          style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
        ),
        SizedBox(height: 4),
        if (data is Map<String, dynamic>)
          ...data.entries.map((entry) => Padding(
            padding: const EdgeInsets.only(left: 8.0),
            child: Text('${entry.key}: ${entry.value}'),
          ))
        else
          Padding(
            padding: const EdgeInsets.only(left: 8.0),
            child: Text(data.toString()),
          ),
      ],
    );
  }
}

/// Widget de erro para casos críticos de inicialização
class ErrorApp extends StatelessWidget {
  final String error;
  
  const ErrorApp({super.key, required this.error});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Baby Tracker - Erro',
      home: Scaffold(
        backgroundColor: Colors.red[50],
        body: Center(
          child: Padding(
            padding: const EdgeInsets.all(16.0),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Icon(Icons.error_outline, size: 64, color: Colors.red),
                SizedBox(height: 16),
                Text(
                  'Erro na Inicialização',
                  style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
                ),
                SizedBox(height: 8),
                Text(
                  'Não foi possível inicializar os serviços de rede.',
                  textAlign: TextAlign.center,
                ),
                SizedBox(height: 16),
                Container(
                  padding: EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: Colors.red[100],
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Text(
                    error,
                    style: TextStyle(fontFamily: 'monospace'),
                  ),
                ),
                SizedBox(height: 16),
                ElevatedButton(
                  onPressed: () {
                    // Reinicia o app
                    main();
                  },
                  child: Text('Tentar Novamente'),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}