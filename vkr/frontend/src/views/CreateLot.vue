<template>
  <div class="create-lot-container">
    <div class="page-header">
      <div class="breadcrumbs">
        <router-link :to="{ name: 'home' }">Главная</router-link>
        <span>/</span>
        <router-link :to="{ name: 'auctions' }">Аукционы</router-link>
        <span>/</span>
        <router-link :to="{ name: 'auction-detail', params: { id: auctionId } }">{{ auctionTitle }}</router-link>
        <span>/</span>
        <span>{{ isEditMode ? 'Редактирование лота' : 'Создание лота' }}</span>
      </div>
      <h1>{{ pageTitle }}</h1>
    </div>
    
    <!-- Индикатор загрузки -->
    <loading-spinner v-if="loading" text="Загрузка данных..." />
    
    <!-- Сообщение об ошибке -->
    <div v-if="error" class="error-message">
      {{ error }}
    </div>
    
    <!-- Форма создания лота -->
    <form v-if="!loading && !success" class="lot-form" @submit.prevent="submitForm">
      <div class="form-group">
        <label for="title">Название лота *</label>
        <input
          type="text"
          id="title"
          v-model="form.title"
          :class="{ 'is-invalid': validation.title }"
          placeholder="Введите название лота"
          required
        >
        <div v-if="validation.title" class="invalid-feedback">
          {{ validation.title }}
        </div>
      </div>
      
      <div class="form-group">
        <label for="description">Описание лота *</label>
        <textarea
          id="description"
          v-model="form.description"
          :class="{ 'is-invalid': validation.description }"
          placeholder="Подробно опишите ваш лот"
          rows="4"
          required
        ></textarea>
        <div v-if="validation.description" class="invalid-feedback">
          {{ validation.description }}
        </div>
      </div>
      
      <div class="form-row">
        <div class="form-group full-width">
          <label for="start_price">Стартовая цена (руб.) *</label>
          <input
            type="number"
            id="start_price"
            v-model="form.start_price"
            :class="{ 'is-invalid': validation.start_price }"
            placeholder="Введите стартовую цену"
            min="1"
            required
          >
          <div v-if="validation.start_price" class="invalid-feedback">
            {{ validation.start_price }}
          </div>
        </div>
      </div>
      
      <div class="form-group">
        <label for="image">Изображение лота {{ !isEditMode ? '*' : '' }}</label>
        <div class="image-upload-container">
          <div v-if="imagePreview" class="image-preview">
            <img :src="imagePreview" alt="Превью">
            <button type="button" class="btn-remove-image" @click="removeImage">✕</button>
          </div>
          <div v-if="!imagePreview" class="image-dropzone">
            <input
              type="file"
              id="image"
              @change="handleImageChange"
              accept="image/*"
              :class="{ 'is-invalid': validation.image }"
            >
            <label for="image" class="dropzone-label">
              <span>Нажмите для выбора изображения</span>
              <span>или перетащите файл сюда</span>
            </label>
          </div>
          <div v-if="validation.image" class="invalid-feedback">
            {{ validation.image }}
          </div>
        </div>
      </div>
      
      <div class="form-actions">
        <button type="button" @click="goBack" class="btn-secondary">
          Отмена
        </button>
        <button
          type="submit"
          class="btn-primary"
          :disabled="submitting"
        >
          {{ submitButtonText }}
        </button>
      </div>
    </form>
    
    <!-- Успешное создание -->
    <div v-if="success" class="success-message">
      <h3>{{ isEditMode ? 'Лот успешно обновлен!' : 'Лот успешно создан!' }}</h3>
      <p>{{ isEditMode ? 'Ваш лот был обновлен.' : 'Ваш лот отправлен на модерацию и будет опубликован после проверки.' }}</p>
      <button @click="goToAuction" class="btn-primary">
        Вернуться к аукциону
      </button>
    </div>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useLotsStore } from '../store/lotsStore';
import { useAuctionsStore } from '../store/auctionsStore';
import { useAuthStore } from '../store/auth';
import LoadingSpinner from '../components/LoadingSpinner.vue';
import lotsApi from '../api/lotsApi';

export default {
  name: 'CreateLotView',
  
  components: {
    LoadingSpinner
  },
  
  setup() {
    const route = useRoute();
    const router = useRouter();
    const lotsStore = useLotsStore();
    const auctionsStore = useAuctionsStore();
    const authStore = useAuthStore();
    
    // Состояния
    const loading = ref(true);
    const error = ref(null);
    const success = ref(false);
    const submitting = ref(false);
    const imagePreview = ref(null);
    const imageFile = ref(null);
    const isEditMode = ref(false);
    const lot = ref(null); // Данные лота для редактирования
    
    // Получение параметров из URL
    const auctionId = computed(() => route.query.auctionId || null);
    const lotId = computed(() => route.query.lotId || null);
    const isEdit = computed(() => route.query.edit === 'true');
    
    // Название аукциона
    const auctionTitle = computed(() => {
      return auctionsStore.currentAuction?.title || 'Аукцион';
    });
    
    // Заголовок страницы
    const pageTitle = computed(() => {
      return isEditMode.value ? 'Редактирование лота' : 'Создание нового лота';
    });
    
    // Заголовок кнопки отправки
    const submitButtonText = computed(() => {
      if (submitting.value) {
        return isEditMode.value ? 'Сохранение...' : 'Создание...';
      }
      return isEditMode.value ? 'Сохранить изменения' : 'Создать лот';
    });
    
    // Форма создания лота
    const form = reactive({
      title: '',
      description: '',
      start_price: '',
      estimate_max: '',
      auction: auctionId.value
    });
    
    // Валидация формы
    const validation = reactive({
      title: '',
      description: '',
      start_price: '',
      estimate_max: '',
      image: ''
    });
    
    // Проверка наличия роли донора
    const checkDonorPermission = () => {
      if (!authStore.isAuthenticated) {
        router.push({ name: 'login' });
        return false;
      }
      
      if (authStore.user?.role !== 'donor') {
        error.value = 'Только доноры могут создавать лоты';
        return false;
      }
      
      return true;
    };
    
    // Загрузка данных лота для редактирования
    const loadLotData = async () => {
      try {
        const lotData = await lotsStore.fetchLotById(lotId.value);
        if (!lotData) {
          error.value = 'Не удалось загрузить данные лота';
          return false;
        }
        
        // Сохраняем данные лота
        lot.value = lotData;
        
        // Проверяем, принадлежит ли лот текущему пользователю
        const isDonorOwner = lotData.donor === authStore.user.id || 
                            lotData.donor_username === authStore.user.username;
        
        if (!isDonorOwner) {
          error.value = 'У вас нет прав на редактирование этого лота';
          return false;
        }
        
        // Проверяем статус лота (можно редактировать только лоты со статусом "pending")
        if (lotData.status !== 'pending') {
          error.value = 'Можно редактировать только лоты со статусом "На рассмотрении"';
          return false;
        }
        
        // Заполняем форму данными лота
        form.title = lotData.title || '';
        form.description = lotData.description || '';
        form.start_price = lotData.starting_price || '';
        form.auction = lotData.auction;
        
        // Если есть изображение, загружаем превью
        if (lotData.images && lotData.images.length > 0) {
          if (lotData.images[0].image_url) {
            imagePreview.value = lotData.images[0].image_url + '?v=' + lotData.images[0].id;
          } else if (lotData.images[0].image) {
            imagePreview.value = lotData.images[0].image.startsWith('http') 
              ? lotData.images[0].image + '?v=' + lotData.images[0].id
              : `http://localhost:8000${lotData.images[0].image}?v=${lotData.images[0].id}`;
          }
        }
        
        return true;
      } catch (err) {
        console.error('Error loading lot data:', err);
        error.value = 'Ошибка при загрузке данных лота';
        return false;
      }
    };
    
    // Загрузка данных аукциона
    const loadInitialData = async () => {
      loading.value = true;
      error.value = null;
      
      try {
        // Проверка доступа
        if (!checkDonorPermission()) {
          loading.value = false;
          return;
        }
        
        // Определяем, находимся ли мы в режиме редактирования
        if (lotId.value && isEdit.value) {
          isEditMode.value = true;
          
          // Загружаем данные лота для редактирования
          const success = await loadLotData();
          if (!success) {
            loading.value = false;
            return;
          }
        } else {
          // Проверка ID аукциона в режиме создания
          if (!auctionId.value) {
            error.value = 'Не указан ID аукциона';
            loading.value = false;
            return;
          }
        }
        
        // Загрузка данных аукциона, если нет в хранилище
        if (!auctionsStore.currentAuction) {
          const auctionData = await auctionsStore.fetchAuctionById(auctionId.value);
          if (!auctionData) {
            error.value = 'Аукцион не найден';
            return;
          }
        }
      } catch (err) {
        error.value = 'Ошибка при загрузке данных';
        console.error('Error loading initial data:', err);
      } finally {
        loading.value = false;
      }
    };
    
    // Обработка изменения изображения
    const handleImageChange = (event) => {
      const file = event.target.files[0];
      if (!file) return;
      
      // Проверка размера (не более 5 МБ)
      if (file.size > 5 * 1024 * 1024) {
        validation.image = 'Размер изображения не должен превышать 5 МБ';
        return;
      }
      
      // Проверка типа файла
      if (!file.type.match('image.*')) {
        validation.image = 'Пожалуйста, выберите изображение';
        return;
      }
      
      // Сохранение файла и создание превью
      imageFile.value = file;
      validation.image = '';
      
      const reader = new FileReader();
      reader.onload = (e) => {
        imagePreview.value = e.target.result;
      };
      reader.readAsDataURL(file);
    };
    
    // Удаление выбранного изображения
    const removeImage = () => {
      imageFile.value = null;
      imagePreview.value = null;
      const input = document.getElementById('image');
      if (input) input.value = '';
    };
    
    // Валидация формы
    const validateForm = () => {
      let isValid = true;
      
      // Очистка предыдущих ошибок
      Object.keys(validation).forEach(key => {
        validation[key] = '';
      });
      
      // Проверка заголовка
      if (!form.title.trim()) {
        validation.title = 'Название лота обязательно';
        isValid = false;
      } else if (form.title.length > 100) {
        validation.title = 'Название лота не должно превышать 100 символов';
        isValid = false;
      }
      
      // Проверка описания
      if (!form.description.trim()) {
        validation.description = 'Описание лота обязательно';
        isValid = false;
      }
      
      // Проверка стартовой цены
      if (!form.start_price) {
        validation.start_price = 'Стартовая цена обязательна';
        isValid = false;
      } else if (Number(form.start_price) <= 0) {
        validation.start_price = 'Стартовая цена должна быть положительным числом';
        isValid = false;
      }
      
      // Проверка максимальной оценочной стоимости
      if (form.estimate_max && Number(form.estimate_max) <= Number(form.start_price)) {
        validation.estimate_max = 'Максимальная оценочная стоимость должна быть больше стартовой цены';
        isValid = false;
      }
      
      return isValid;
    };
    
    // Отправка формы
    const submitForm = async () => {
      if (!validateForm()) return;
      
      submitting.value = true;
      
      try {
        let response;
        
        // Подготовка данных формы
        const lotData = {
          title: form.title,
          description: form.description,
          starting_price: parseFloat(form.start_price),
          auction: parseInt(auctionId.value) // Убедимся, что аукцион передается как число
        };
        
        console.log("Данные лота для отправки на сервер:", lotData);
        
        // Проверка, что указан ID аукциона
        if (!lotData.auction) {
          error.value = 'Не указан ID аукциона для привязки лота';
          submitting.value = false;
          return;
        }
        
        if (isEditMode.value) {
          // Обновление существующего лота
          console.log(`Обновление лота с ID ${lotId.value}`);
          response = await lotsStore.updateLot(lotId.value, lotData);
        } else {
          // Создание нового лота
          console.log(`Создание нового лота для аукциона с ID ${auctionId.value}`);
          response = await lotsStore.createLot(lotData);
        }
        
        if (response) {
          // Если есть новое изображение, загружаем его
          if (imageFile.value) {
            try {
              // Для новых лотов или обновления существующих
              const lotIdToUse = isEditMode.value ? lotId.value : response.id;
              
              // Если редактируем лот и удалили исходное изображение, сначала удаляем старое изображение
              if (isEditMode.value && lot.value && lot.value.images && lot.value.images.length > 0) {
                // Попытка удалить старое изображение перед загрузкой нового
                try {
                  const imageId = lot.value.images[0].id;
                  if (imageId) {
                    await lotsStore.deleteImage(imageId);
                  }
                } catch (deleteError) {
                  console.error('Ошибка при удалении старого изображения:', deleteError);
                  // Продолжаем загрузку даже если удаление не удалось
                }
              }
              
              // Загружаем новое изображение
              await lotsStore.uploadImage(lotIdToUse, imageFile.value);
              
              // Небольшая задержка, чтобы сервер успел обработать изображение
              await new Promise(resolve => setTimeout(resolve, 500));
              
              // Если мы в режиме редактирования, обновляем данные лота
              if (isEditMode.value) {
                await lotsStore.fetchLotById(lotId.value);
              }
            } catch (imageError) {
              console.error('Ошибка при загрузке изображения:', imageError);
              // Продолжаем выполнение, даже если изображение не загрузилось
            }
          }
          
          // Дополнительная задержка перед отображением сообщения об успехе
          // для обеспечения завершения всех операций на сервере
          await new Promise(resolve => setTimeout(resolve, 500));
          
          success.value = true;
        } else {
          error.value = lotsStore.error || `Ошибка при ${isEditMode.value ? 'обновлении' : 'создании'} лота`;
        }
      } catch (err) {
        error.value = 'Ошибка при отправке данных';
        console.error('Error submitting form:', err);
      } finally {
        submitting.value = false;
      }
    };
    
    // Возврат к странице аукциона
    const goToAuction = () => {
      router.push({ name: 'auction-detail', params: { id: auctionId.value } });
    };
    
    // Функция возврата
    const goBack = () => {
      router.back();
    };
    
    // Загрузка начальных данных при монтировании компонента
    onMounted(() => {
      loadInitialData();
    });
    
    return {
      form,
      loading,
      error,
      success,
      submitting,
      validation,
      imagePreview,
      auctionId,
      auctionTitle,
      isEditMode,
      pageTitle,
      submitButtonText,
      handleImageChange,
      removeImage,
      submitForm,
      goToAuction,
      goBack,
      lot
    };
  }
}
</script>

<style scoped>
.create-lot-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 24px;
}

.page-header {
  margin-bottom: 32px;
}

h1 {
  margin-bottom: 8px;
  color: #333;
}

.breadcrumbs {
  color: #6c757d;
  font-size: 14px;
  margin-bottom: 16px;
}

.breadcrumbs a {
  color: #007bff;
  text-decoration: none;
}

.breadcrumbs a:hover {
  text-decoration: underline;
}

.breadcrumbs span {
  margin: 0 8px;
}

.lot-form {
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  padding: 24px;
}

.form-group {
  margin-bottom: 20px;
}

.form-row {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
}

.full-width {
  flex: 1;
  margin-bottom: 0;
}

label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: #333;
}

input[type="text"],
input[type="number"],
textarea,
select {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #ced4da;
  border-radius: 4px;
  font-size: 16px;
  transition: border-color 0.3s;
}

input:focus,
textarea:focus,
select:focus {
  border-color: #007bff;
  outline: none;
}

.is-invalid {
  border-color: #dc3545;
}

.invalid-feedback {
  color: #dc3545;
  font-size: 14px;
  margin-top: 5px;
}

.image-upload-container {
  margin-top: 8px;
}

.image-preview {
  margin-top: 16px;
  position: relative;
  display: inline-block;
}

.image-preview img {
  max-width: 100%;
  max-height: 200px;
  border-radius: 4px;
}

.btn-remove-image {
  position: absolute;
  top: 8px;
  right: 8px;
  background-color: rgba(220, 53, 69, 0.9);
  color: white;
  border: none;
  border-radius: 50%;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  font-size: 14px;
  font-weight: bold;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.status-info {
  background-color: #e2f0fd;
  padding: 12px;
  border-radius: 4px;
  margin: 24px 0;
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 14px;
  color: #0d6efd;
}

.info-icon {
  font-size: 20px;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 16px;
  margin-top: 24px;
}

.btn-primary,
.btn-secondary {
  padding: 10px 24px;
  border-radius: 4px;
  font-weight: 500;
  cursor: pointer;
  border: none;
  transition: background-color 0.3s;
}

.btn-primary {
  background-color: #28a745;
  color: white;
}

.btn-primary:hover {
  background-color: #218838;
}

.btn-primary:disabled {
  background-color: #7fad89;
  cursor: not-allowed;
}

.btn-secondary {
  background-color: #6c757d;
  color: white;
}

.btn-secondary:hover {
  background-color: #5a6268;
}

.error-message {
  background-color: #f8d7da;
  color: #721c24;
  padding: 16px;
  border-radius: 8px;
  margin-bottom: 24px;
  text-align: center;
}

.success-message {
  background-color: #d4edda;
  color: #155724;
  padding: 24px;
  border-radius: 8px;
  text-align: center;
}

.success-message h3 {
  margin-bottom: 8px;
}

.success-message p {
  margin-bottom: 20px;
}

@media (max-width: 768px) {
  .form-row {
    flex-direction: column;
    gap: 16px;
  }
  
  .full-width {
    width: 100%;
  }
  
  .form-actions {
    flex-direction: column-reverse;
  }
  
  .btn-primary,
  .btn-secondary {
    width: 100%;
  }
}
</style> 