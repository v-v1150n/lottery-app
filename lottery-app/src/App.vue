<script setup>
import { ref, computed } from 'vue'

// 狀態
const isSpinning = ref(false)
const showList = ref(false)
const displayName = ref('')
const displayDept = ref('')
const winner = ref(null)
const winners = ref([])
const participants = ref([])
const fileLoaded = ref(false)
const fileName = ref('')

// 可抽獎名單（排除已中獎者）
const availableParticipants = computed(() => 
  participants.value.filter(p => !winners.value.some(w => w.name === p.name && w.dept === p.dept))
)

// 上傳檔案
const handleFileUpload = (event) => {
  const file = event.target.files[0]
  if (!file) return
  
  fileName.value = file.name
  const reader = new FileReader()
  
  reader.onload = (e) => {
    const text = e.target.result
    const lines = text.split('\n').filter(line => line.trim())
    const startIndex = lines[0].includes('姓名') ? 1 : 0
    
    participants.value = lines.slice(startIndex).map(line => {
      const [name, dept] = line.split('\t')
      return { name: name?.trim() || '', dept: dept?.trim() || '' }
    }).filter(p => p.name)
    
    fileLoaded.value = true
    winners.value = []
    winner.value = null
    displayName.value = ''
    displayDept.value = ''
  }
  
  reader.readAsText(file, 'UTF-8')
}

// 抽獎動畫
const startLottery = () => {
  if (isSpinning.value || availableParticipants.value.length === 0) return
  
  isSpinning.value = true
  winner.value = null
  
  const duration = 3000 + Math.random() * 2000
  const startTime = Date.now()
  
  const animate = () => {
    const elapsed = Date.now() - startTime
    if (elapsed < duration) {
      const speed = Math.max(50, 300 * (elapsed / duration))
      const randomPerson = availableParticipants.value[Math.floor(Math.random() * availableParticipants.value.length)]
      displayName.value = randomPerson.name
      displayDept.value = randomPerson.dept
      setTimeout(animate, speed)
    } else {
      const finalWinner = availableParticipants.value[Math.floor(Math.random() * availableParticipants.value.length)]
      displayName.value = finalWinner.name
      displayDept.value = finalWinner.dept
      winner.value = finalWinner
      winners.value.push(finalWinner)
      isSpinning.value = false
    }
  }
  
  animate()
}

// 重置抽獎
const resetLottery = () => {
  winners.value = []
  winner.value = null
  displayName.value = ''
  displayDept.value = ''
}

// 清除檔案
const clearFile = () => {
  fileLoaded.value = false
  fileName.value = ''
  participants.value = []
  winners.value = []
  winner.value = null
  displayName.value = ''
  displayDept.value = ''
}
</script>

<template>
  <div class="app">
    <!-- 左右幕布裝飾 -->
    <div class="curtain curtain-left"></div>
    <div class="curtain curtain-right"></div>
    
    <div class="container">
      <h1 class="title">🎬 忘年會 David 最大獎 🎬</h1>
      
      <!-- 上傳區 -->
      <div class="upload-section" v-if="!fileLoaded">
        <div class="marquee-frame">
          <div class="marquee-lights">
            <span v-for="n in 20" :key="n" class="light"></span>
          </div>
          <div class="upload-box">
            <input 
              type="file" 
              id="file-input" 
              accept=".txt" 
              @change="handleFileUpload"
              hidden
            />
            <label for="file-input" class="upload-label">
              <span class="upload-icon">📁</span>
              <span class="upload-text">點擊上傳名單檔案 (.txt)</span>
              <span class="upload-hint">格式：姓名[Tab]部門</span>
            </label>
          </div>
        </div>
      </div>
      
      <!-- 主抽獎區 -->
      <template v-else>
        <!-- 檔案資訊 -->
        <div class="file-info">
          <span class="file-name">📄 {{ fileName }}</span>
          <button class="btn-clear" @click="clearFile">✕ 更換檔案</button>
        </div>
        
        <!-- 抽獎區 - 跑馬燈框 -->
        <div class="marquee-frame lottery-frame" :class="{ spinning: isSpinning, winner: winner }">
          <div class="marquee-lights">
            <span v-for="n in 24" :key="n" class="light"></span>
          </div>
          <div class="display-area">
            <div class="name" :class="{ animate: isSpinning }">
              {{ displayName || '？？？' }}
            </div>
            <div class="dept" v-if="displayDept">
              {{ displayDept }}
            </div>
          </div>
        </div>
        
        <!-- 按鈕區 -->
        <div class="button-group">
          <button 
            class="btn primary" 
            @click="startLottery" 
            :disabled="isSpinning || availableParticipants.length === 0"
          >
            {{ isSpinning ? '抽獎中...' : '🎰 開始抽獎' }}
          </button>
          <button class="btn secondary" @click="showList = !showList">
            📋 {{ showList ? '隱藏名單' : '查看名單' }}
          </button>
          <button class="btn danger" @click="resetLottery" :disabled="isSpinning">
            🔄 重新開始
          </button>
        </div>
        
        <!-- 統計 -->
        <div class="stats">
          <span>✦ 總人數：{{ participants.length }}</span>
          <span>✦ 剩餘：{{ availableParticipants.length }}</span>
          <span>✦ 已抽：{{ winners.length }}</span>
        </div>
        
        <!-- 中獎名單 -->
        <div class="winners-section" v-if="winners.length > 0">
          <h3>🏆 中獎名單</h3>
          <div class="winners-list">
            <div class="winner-item" v-for="(w, i) in winners" :key="i">
              <span class="rank">{{ i + 1 }}</span>
              <span class="winner-name">{{ w.name }}</span>
              <span class="winner-dept">{{ w.dept }}</span>
            </div>
          </div>
        </div>
        
        <!-- 名單檢視 -->
        <div class="list-section" v-if="showList">
          <h3>📋 抽獎名單 ({{ participants.length }} 人)</h3>
          <div class="participant-list">
            <div 
              class="participant-item" 
              v-for="(p, i) in participants" 
              :key="i"
              :class="{ drawn: winners.some(w => w.name === p.name && w.dept === p.dept) }"
            >
              <span class="num">{{ i + 1 }}</span>
              <span class="p-name">{{ p.name }}</span>
              <span class="p-dept">{{ p.dept }}</span>
            </div>
          </div>
        </div>
      </template>
    </div>
  </div>
</template>

<style>
/* 左右幕布 */
.curtain {
  position: fixed;
  top: 0;
  bottom: 0;
  width: 120px;
  background: linear-gradient(90deg,
    #3a0a0a 0%,
    #6a1515 30%,
    #8b2020 50%,
    #6a1515 70%,
    #3a0a0a 100%
  );
  z-index: 10;
  pointer-events: none;
}

.curtain::before {
  content: '';
  position: absolute;
  top: 0;
  bottom: 0;
  width: 100%;
  background: repeating-linear-gradient(
    180deg,
    transparent 0px,
    transparent 20px,
    rgba(0,0,0,0.1) 20px,
    rgba(0,0,0,0.1) 40px
  );
}

.curtain-left {
  left: 0;
  border-right: 3px solid #c9a227;
  box-shadow: inset -20px 0 30px rgba(0,0,0,0.3);
}

.curtain-right {
  right: 0;
  border-left: 3px solid #c9a227;
  box-shadow: inset 20px 0 30px rgba(0,0,0,0.3);
}

.app {
  min-height: 100vh;
  padding: 40px 140px;
}

.container {
  max-width: 1200px;
  width: 100%;
  margin: 0 auto;
  padding: 0 40px;
}

.title {
  text-align: center;
  font-size: 3.5rem;
  color: #f5e6c8;
  text-shadow: 
    3px 3px 0 #8b4513,
    -1px -1px 0 #8b4513,
    1px -1px 0 #8b4513,
    -1px 1px 0 #8b4513;
  margin-bottom: 50px;
  font-weight: bold;
  letter-spacing: 8px;
}

/* 跑馬燈框 */
.marquee-frame {
  position: relative;
  background: linear-gradient(145deg, #1a1a2e, #0d0d1a);
  border: 8px solid #c9a227;
  border-radius: 20px;
  padding: 50px 40px;
  box-shadow: 
    0 0 30px rgba(201, 162, 39, 0.3),
    inset 0 0 50px rgba(0,0,0,0.5);
}

.marquee-lights {
  position: absolute;
  top: -12px;
  left: -12px;
  right: -12px;
  bottom: -12px;
  pointer-events: none;
}

.light {
  position: absolute;
  width: 16px;
  height: 16px;
  background: radial-gradient(circle, #fff5c0 30%, #c9a227 70%);
  border-radius: 50%;
  box-shadow: 0 0 10px #ffd700, 0 0 20px rgba(255, 215, 0, 0.5);
  animation: lightBlink 1s ease-in-out infinite alternate;
}

.light:nth-child(odd) {
  animation-delay: 0.5s;
}

/* 燈泡位置分布 */
.marquee-lights .light:nth-child(1) { top: 0; left: 10%; }
.marquee-lights .light:nth-child(2) { top: 0; left: 25%; }
.marquee-lights .light:nth-child(3) { top: 0; left: 40%; }
.marquee-lights .light:nth-child(4) { top: 0; left: 55%; }
.marquee-lights .light:nth-child(5) { top: 0; left: 70%; }
.marquee-lights .light:nth-child(6) { top: 0; left: 85%; }
.marquee-lights .light:nth-child(7) { bottom: 0; left: 10%; }
.marquee-lights .light:nth-child(8) { bottom: 0; left: 25%; }
.marquee-lights .light:nth-child(9) { bottom: 0; left: 40%; }
.marquee-lights .light:nth-child(10) { bottom: 0; left: 55%; }
.marquee-lights .light:nth-child(11) { bottom: 0; left: 70%; }
.marquee-lights .light:nth-child(12) { bottom: 0; left: 85%; }
.marquee-lights .light:nth-child(13) { left: 0; top: 15%; }
.marquee-lights .light:nth-child(14) { left: 0; top: 40%; }
.marquee-lights .light:nth-child(15) { left: 0; top: 65%; }
.marquee-lights .light:nth-child(16) { left: 0; top: 85%; }
.marquee-lights .light:nth-child(17) { right: 0; top: 15%; }
.marquee-lights .light:nth-child(18) { right: 0; top: 40%; }
.marquee-lights .light:nth-child(19) { right: 0; top: 65%; }
.marquee-lights .light:nth-child(20) { right: 0; top: 85%; }
.marquee-lights .light:nth-child(21) { top: 0; left: 5%; }
.marquee-lights .light:nth-child(22) { top: 0; right: 5%; }
.marquee-lights .light:nth-child(23) { bottom: 0; left: 5%; }
.marquee-lights .light:nth-child(24) { bottom: 0; right: 5%; }

@keyframes lightBlink {
  0% { opacity: 0.6; box-shadow: 0 0 5px #ffd700; }
  100% { opacity: 1; box-shadow: 0 0 15px #ffd700, 0 0 30px rgba(255, 215, 0, 0.6); }
}

.lottery-frame.spinning .light {
  animation-duration: 0.3s;
}

.lottery-frame.winner .light {
  background: radial-gradient(circle, #fff 30%, #ffd700 70%);
  animation-duration: 0.2s;
}

/* 上傳區 */
.upload-section {
  display: flex;
  justify-content: center;
  margin-top: 60px;
}

.upload-box {
  width: 100%;
}

.upload-label {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.upload-label:hover {
  transform: scale(1.02);
}

.upload-icon {
  font-size: 4rem;
  margin-bottom: 20px;
}

.upload-text {
  font-size: 1.8rem;
  color: #f5e6c8;
  margin-bottom: 10px;
  font-weight: bold;
}

.upload-hint {
  font-size: 1rem;
  color: #c9a227;
}

/* 檔案資訊 */
.file-info {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 15px;
  margin-bottom: 30px;
  padding: 10px 25px;
  background: rgba(139, 69, 19, 0.4);
  border: 2px solid #c9a227;
  border-radius: 50px;
}

.file-name {
  color: #f5e6c8;
  font-size: 1.1rem;
}

.btn-clear {
  background: transparent;
  border: 1px solid #f5e6c8;
  color: #f5e6c8;
  padding: 5px 15px;
  border-radius: 20px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: all 0.3s ease;
}

.btn-clear:hover {
  background: #8b4513;
}

/* 抽獎顯示區 */
.display-area {
  min-height: 150px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
}

.name {
  font-size: 5rem;
  font-weight: bold;
  color: #f5e6c8;
  letter-spacing: 15px;
  text-shadow: 
    3px 3px 0 #8b4513,
    0 0 20px rgba(245, 230, 200, 0.3);
}

.name.animate {
  animation: flash 0.1s infinite;
}

@keyframes flash {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.7; }
}

.dept {
  font-size: 1.8rem;
  color: #c9a227;
  margin-top: 20px;
  font-weight: bold;
}

/* 按鈕 */
.button-group {
  display: flex;
  gap: 20px;
  justify-content: center;
  margin-top: 50px;
  flex-wrap: wrap;
}

.btn {
  padding: 18px 45px;
  font-size: 1.3rem;
  border: 3px solid #c9a227;
  border-radius: 50px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-weight: bold;
  text-shadow: 1px 1px 2px rgba(0,0,0,0.3);
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn.primary {
  background: linear-gradient(135deg, #c9a227, #8b6914);
  color: #1a0a0a;
  box-shadow: 0 5px 20px rgba(201, 162, 39, 0.4);
}

.btn.primary:hover:not(:disabled) {
  transform: translateY(-3px);
  box-shadow: 0 8px 30px rgba(201, 162, 39, 0.6);
}

.btn.secondary {
  background: linear-gradient(135deg, #8b2020, #5a1515);
  color: #f5e6c8;
}

.btn.secondary:hover {
  transform: translateY(-3px);
  background: linear-gradient(135deg, #a02828, #6a1a1a);
}

.btn.danger {
  background: linear-gradient(135deg, #4a3728, #2a1a10);
  color: #f5e6c8;
}

.btn.danger:hover:not(:disabled) {
  transform: translateY(-3px);
}

/* 統計 */
.stats {
  display: flex;
  justify-content: center;
  gap: 40px;
  margin-top: 35px;
  color: #f5e6c8;
  font-size: 1.2rem;
  font-weight: bold;
}

/* 中獎名單 */
.winners-section, .list-section {
  margin-top: 50px;
  background: rgba(26, 10, 10, 0.7);
  border: 3px solid #c9a227;
  border-radius: 15px;
  padding: 30px;
}

.winners-section h3, .list-section h3 {
  color: #f5e6c8;
  margin-bottom: 25px;
  text-align: center;
  font-size: 1.5rem;
  text-shadow: 2px 2px 0 #8b4513;
}

.winners-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.winner-item {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 15px 25px;
  background: linear-gradient(135deg, rgba(201, 162, 39, 0.2), rgba(139, 69, 19, 0.2));
  border-radius: 10px;
  border-left: 5px solid #c9a227;
}

.rank {
  width: 35px;
  height: 35px;
  background: linear-gradient(135deg, #c9a227, #8b6914);
  color: #1a0a0a;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  font-size: 1.1rem;
}

.winner-name {
  font-size: 1.4rem;
  color: #f5e6c8;
  font-weight: bold;
}

.winner-dept {
  color: #c9a227;
  margin-left: auto;
  font-weight: bold;
}

/* 名單 */
.participant-list {
  max-height: 400px;
  overflow-y: auto;
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 10px;
}

.participant-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 15px;
  background: rgba(139, 69, 19, 0.2);
  border-radius: 8px;
  border: 1px solid rgba(201, 162, 39, 0.3);
  transition: all 0.3s ease;
}

.participant-item.drawn {
  opacity: 0.4;
  text-decoration: line-through;
}

.num {
  color: #c9a227;
  font-size: 0.9rem;
  min-width: 25px;
}

.p-name {
  color: #f5e6c8;
  font-weight: 500;
}

.p-dept {
  color: #c9a227;
  font-size: 0.85rem;
  margin-left: auto;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 140px;
}

/* 自訂滾動條 */
.participant-list::-webkit-scrollbar {
  width: 8px;
}

.participant-list::-webkit-scrollbar-track {
  background: rgba(0,0,0,0.3);
  border-radius: 4px;
}

.participant-list::-webkit-scrollbar-thumb {
  background: #c9a227;
  border-radius: 4px;
}
</style>
