# 📊 Baby Tracker - Modelos do Banco de Dados

## 🏗️ Arquitetura dos Modelos

Este documento descreve todos os modelos SQLAlchemy criados para o Baby Tracker.

## 📋 Modelos Implementados

### 1. 👤 **User** (`users`)
Representa os usuários (pais/cuidadores) do sistema.

**Campos principais:**
- `email` - Email único do usuário
- `username` - Nome de usuário único  
- `full_name` - Nome completo
- `hashed_password` - Senha criptografada
- `is_active` - Status ativo/inativo
- `is_verified` - Email verificado

**Relacionamentos:**
- `babies` - Um usuário pode ter múltiplos bebês

### 2. 👶 **Baby** (`babies`)
Representa os bebês cadastrados no sistema.

**Campos principais:**
- `name` - Nome do bebê
- `birth_date` - Data de nascimento
- `gender` - Gênero (male/female/other)
- `birth_weight` - Peso ao nascer (gramas)
- `birth_height` - Altura ao nascer (cm)
- `notes` - Observações gerais

**Relacionamentos:**
- `user` - Pertence a um usuário
- `feedings` - Múltiplos registros de alimentação
- `sleep_records` - Múltiplos registros de sono
- `photos` - Múltiplas fotos
- `diaper_changes` - Múltiplas trocas de fralda

### 3. 🍼 **Feeding** (`feedings`)
Registra as alimentações do bebê.

**Tipos de alimentação:**
- `BREASTFEEDING` - Amamentação
- `BOTTLE` - Mamadeira
- `SOLID_FOOD` - Comida sólida

**Campos específicos:**
- `start_time/end_time` - Horários início/fim
- `breast_side` - Lado do seio (left/right/both)
- `bottle_amount` - Quantidade mamadeira (ml)
- `food_description` - Descrição comida sólida

**Propriedades calculadas:**
- `duration_minutes` - Duração em minutos

### 4. 😴 **Sleep** (`sleep_records`)
Registra os períodos de sono do bebê.

**Tipos de sono:**
- `NAP` - Soneca
- `NIGHT_SLEEP` - Sono noturno

**Qualidade do sono:**
- `EXCELLENT` (5⭐) - Excelente
- `GOOD` (4⭐) - Bom
- `AVERAGE` (3⭐) - Médio
- `POOR` (2⭐) - Ruim
- `VERY_POOR` (1⭐) - Muito ruim

**Propriedades calculadas:**
- `duration_minutes` - Duração em minutos
- `duration_hours` - Duração formatada (2h 30m)
- `is_active` - Se o sono está em andamento

### 5. 📷 **Photo** (`photos`)
Armazena fotos do bebê com metadados.

**Campos de arquivo:**
- `filename` - Nome do arquivo processado
- `original_filename` - Nome original
- `s3_url` - URL completa no S3
- `s3_key` - Chave do arquivo no S3
- `file_size` - Tamanho em bytes
- `content_type` - Tipo MIME

**Campos contextuais:**
- `caption` - Legenda da foto
- `is_milestone` - Marco importante
- `milestone_description` - Descrição do marco
- `photo_taken_at` - Data que a foto foi tirada

**Propriedades calculadas:**
- `file_size_mb` - Tamanho em MB

### 6. 🍼 **Diaper** (`diaper_changes`)
Registra as trocas de fralda.

**Tipos de fralda:**
- `WET` - Apenas xixi
- `DIRTY` - Apenas cocô  
- `MIXED` - Ambos

**Consistência do cocô:**
- `LIQUID` - Líquido
- `SOFT` - Mole
- `FORMED` - Formado
- `HARD` - Duro

**Cor do cocô:**
- `YELLOW` - Amarelo (normal)
- `BROWN` - Marrom (normal)
- `GREEN` - Verde
- `BLACK` - Preto (mecônio/preocupante)
- `RED` - Vermelho (sangue)
- `WHITE` - Branco (preocupante)

**Campos adicionais:**
- `has_rash` - Tem assadura
- `applied_cream` - Aplicou pomada

**Propriedades calculadas:**
- `has_stool` - Tem cocô
- `has_urine` - Tem xixi

## 🔗 Relacionamentos

```
User (1) ←→ (N) Baby
Baby (1) ←→ (N) Feeding
Baby (1) ←→ (N) Sleep
Baby (1) ←→ (N) Photo  
Baby (1) ←→ (N) Diaper
```

## 🧪 Como Testar

1. **Certifique-se que o PostgreSQL está rodando:**
```bash
cd docker
docker-compose up -d db
```

2. **Execute o script de teste:**
```bash
cd backend
python test_models.py
```

3. **Verifique no pgAdmin:**
- Acesse: http://localhost:8080
- Login: admin@baby-tracker.com / admin123

## 📝 Timestamps Autom