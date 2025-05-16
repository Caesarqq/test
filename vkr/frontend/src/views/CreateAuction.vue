<template>
  <div class="create-auction-container">
    <h1>Создание нового аукциона</h1>
    
    <!-- Индикатор загрузки -->
    <loading-spinner v-if="loading" text="Создание аукциона..." />
    
    <!-- Сообщение об ошибке -->
    <alert-message 
      v-if="error" 
      :show="!!error" 
      :message="error" 
      type="error" 
      :auto-hide="false"
      @close="error = null" 
      class="error-alert"
    />
    
    <!-- Сообщение об успехе -->
    <alert-message 
      v-if="success" 
      :show="success" 
      message="Аукцион успешно создан! Вы будете перенаправлены на страницу аукционов." 
      type="success" 
      :auto-hide="true"
      :duration="3000"
    />
    
    <!-- Форма создания аукциона -->
    <form v-if="!loading && !success" @submit.prevent="createAuction" class="auction-form" enctype="multipart/form-data">
      <!-- Общее сообщение о необходимости заполнить все поля -->
      <div class="form-notice">
        <p>Все поля, отмеченные *, обязательны для заполнения</p>
      </div>
      
      <div class="form-group">
        <label for="title">Название аукциона*</label>
        <input 
          type="text" 
          id="title" 
          v-model="form.title" 
          required 
          placeholder="Например: Благотворительный аукцион в поддержку детского дома"
          :class="{ 'is-invalid': validation.title }"
        />
        <div v-if="validation.title" class="invalid-feedback">
          {{ validation.title }}
        </div>
      </div>
      
      <div class="form-group">
        <label for="description">Описание аукциона*</label>
        <textarea 
          id="description" 
          v-model="form.description" 
          required 
          rows="5"
          placeholder="Опишите цель аукциона, куда будут направлены собранные средства и т.д."
          :class="{ 'is-invalid': validation.description }"
        ></textarea>
        <div v-if="validation.description" class="invalid-feedback">
          {{ validation.description }}
        </div>
      </div>
      
      <!-- Загрузка изображения -->
      <div class="form-group">
        <label for="image">Изображение аукциона</label>
        <div class="image-upload-container">
          <input 
            type="file" 
            id="image" 
            @change="handleImageUpload" 
            accept="image/*"
            :class="{ 'is-invalid': validation.image }"
          />
          <div class="upload-button" @click="triggerImageInput">
            <span>Выберите изображение</span>
          </div>
          <span v-if="imageFileName" class="file-name">{{ imageFileName }}</span>
        </div>
        <div v-if="validation.image" class="invalid-feedback">
          {{ validation.image }}
        </div>
        
        <!-- Предпросмотр изображения -->
        <div v-if="imagePreview" class="image-preview-container">
          <img :src="imagePreview" alt="Предпросмотр изображения" class="image-preview" />
          <button type="button" class="remove-image-btn" @click="removeImage">×</button>
        </div>
      </div>
      
      <div class="form-row">
        <div class="form-group half">
          <label for="start_date">Дата начала*</label>
          <input 
            type="datetime-local" 
            id="start_date" 
            v-model="form.start_date" 
            required
            :class="{ 'is-invalid': validation.start_date }"
          />
          <div v-if="validation.start_date" class="invalid-feedback">
            {{ validation.start_date }}
          </div>
        </div>
        
        <div class="form-group half">
          <label for="end_date">Дата окончания*</label>
          <input 
            type="datetime-local" 
            id="end_date" 
            v-model="form.end_date" 
            required
            :class="{ 'is-invalid': validation.end_date }"
          />
          <div v-if="validation.end_date" class="invalid-feedback">
            {{ validation.end_date }}
          </div>
        </div>
      </div>
      
      <!-- Добавляем галочку для платного аукциона -->
      <div class="form-group">
        <div class="checkbox-container">
          <input 
            type="checkbox" 
            id="is_paid" 
            v-model="form.is_paid"
          />
          <label for="is_paid">Сделать аукцион платным (требуется покупка билета)</label>
        </div>
      </div>
      
      <!-- Поле для цены билета, показывается только если аукцион платный -->
      <div class="form-group" v-if="form.is_paid">
        <label for="ticket_price">Цена билета (руб.)*</label>
        <input 
          type="number" 
          id="ticket_price" 
          v-model="form.ticket_price" 
          required
          min="1"
          step="0.01"
          :class="{ 'is-invalid': validation.ticket_price }"
        />
        <div v-if="validation.ticket_price" class="invalid-feedback">
          {{ validation.ticket_price }}
        </div>
      </div>
      
      <div class="form-actions">
        <button type="button" @click="goBack" class="btn-secondary">Отмена</button>
        <button type="submit" class="btn-primary" :disabled="loading">
          {{ isEditMode ? 'Сохранить изменения' : 'Создать аукцион' }}
        </button>
      </div>
    </form>
  </div>
</template>

<script>
import { ref, reactive, onMounted, watch } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useAuthStore } from '../store/auth';
import { useAuctionsStore } from '../store/auctionsStore';
import LoadingSpinner from '../components/LoadingSpinner.vue';
import AlertMessage from '../components/AlertMessage.vue';
import apiClient from '../api/axios';
import authApi from '../api/authApi';

export default {
  name: 'CreateAuctionView',
  
  components: {
    LoadingSpinner,
    AlertMessage
  },
  
  setup() {
    const router = useRouter();
    const route = useRoute();
    const authStore = useAuthStore();
    const auctionsStore = useAuctionsStore();
    
    const loading = ref(false);
    const error = ref(null);
    const success = ref(false);
    
    // Переменные для изображения
    const imageFile = ref(null);
    const imagePreview = ref(null);
    const imageFileName = ref('');
    
    // Форма данных аукциона
    const form = reactive({
      title: '',
      description: '',
      start_date: '',
      end_date: '',
      image: null,
      is_paid: false,
      ticket_price: 0
    });
    
    // Валидация формы
    const validation = reactive({
      title: '',
      description: '',
      start_date: '',
      end_date: '',
      image: '',
      ticket_price: ''
    });
    
    // Новый блок: определяем режим и подгружаем данные
    const isEditMode = ref(false);
    const editAuctionId = ref(null);
    
    onMounted(async () => {
      // Проверяем, авторизован ли пользователь
      if (!authStore.isAuthenticated) {
        router.push('/login');
        return;
      }
      
      await authStore.fetchUserProfile();
      
      if (authStore.user?.role !== 'charity') {
        router.push('/auctions');
        return;
      }
      
      // Проверяем режим редактирования
      const editId = route.query.edit;
      if (editId) {
        isEditMode.value = true;
        editAuctionId.value = editId;
        loading.value = true;
        try {
          const auction = await auctionsStore.fetchAuctionById(editId);
          if (auction) {
            form.title = auction.name || '';
            form.description = auction.description || '';
            // Преобразуем ISO-дату в формат для input[type=datetime-local]
            form.start_date = auction.start_time ? auction.start_time.slice(0, 16) : '';
            form.end_date = auction.end_time ? auction.end_time.slice(0, 16) : '';
            // Если есть изображение, показываем превью
            if (auction.image_url) {
              imagePreview.value = auction.image_url;
              imageFileName.value = auction.image_url.split('/').pop();
              form.image = null; // Не отправляем старое изображение
            }
          }
        } catch (e) {
          error.value = 'Ошибка при загрузке данных аукциона';
        } finally {
          loading.value = false;
        }
      } else {
        // Режим создания: значения по умолчанию
        const now = new Date();
        const startDate = new Date(now);
        startDate.setDate(startDate.getDate() + 1);
        form.start_date = formatDateForInput(startDate);
        const endDate = new Date(startDate);
        endDate.setDate(endDate.getDate() + 7);
        form.end_date = formatDateForInput(endDate);
      }
    });
    
    // Обработчик загрузки изображения
    const handleImageUpload = (event) => {
      const file = event.target.files[0];
      if (!file) return;
      
      // Проверяем размер файла (не более 5 МБ)
      const maxSize = 5 * 1024 * 1024; // 5 МБ
      if (file.size > maxSize) {
        validation.image = 'Размер изображения не должен превышать 5 МБ';
        return;
      }
      
      // Проверяем тип файла
      const allowedTypes = ['image/jpeg', 'image/png', 'image/jpg', 'image/gif'];
      if (!allowedTypes.includes(file.type)) {
        validation.image = 'Разрешены только изображения форматов JPEG, PNG, JPG или GIF';
        return;
      }
      
      // Сбрасываем ошибку, если была
      validation.image = '';
      
      // Сохраняем файл
      imageFile.value = file;
      form.image = file;
      imageFileName.value = file.name;
      
      // Создаем предпросмотр
      const reader = new FileReader();
      reader.onload = (e) => {
        imagePreview.value = e.target.result;
      };
      reader.readAsDataURL(file);
    };
    
    // Функция для программного клика на input file
    const triggerImageInput = () => {
      document.getElementById('image').click();
    };
    
    // Удаление изображения
    const removeImage = () => {
      imageFile.value = null;
      imagePreview.value = null;
      imageFileName.value = '';
      form.image = null;
      
      // Сбрасываем значение input file, чтобы можно было выбрать тот же файл повторно
      const fileInput = document.getElementById('image');
      if (fileInput) {
        fileInput.value = '';
      }
    };
    
    // Функция для форматирования даты для input типа datetime-local
    const formatDateForInput = (date) => {
      return date.toISOString().slice(0, 16);
    };
    
    // Валидация формы
    const validateForm = () => {
      let isValid = true;
      // Очищаем предыдущие ошибки
      Object.keys(validation).forEach(key => validation[key] = '');
      
      // Валидация названия
      if (!form.title.trim()) {
        validation.title = 'Название аукциона обязательно';
        isValid = false;
      }
      
      // Валидация описания
      if (!form.description.trim()) {
        validation.description = 'Описание аукциона обязательно';
        isValid = false;
      }
      
      // Валидация даты начала
      if (!form.start_date) {
        validation.start_date = 'Дата начала обязательна';
        isValid = false;
      }
      
      // Валидация даты окончания
      if (!form.end_date) {
        validation.end_date = 'Дата окончания обязательна';
        isValid = false;
      } else if (form.start_date && form.end_date) {
        const startDate = new Date(form.start_date);
        const endDate = new Date(form.end_date);
        
        if (endDate <= startDate) {
          validation.end_date = 'Дата окончания должна быть позже даты начала';
          isValid = false;
        }
      }
      
      // Валидация цены билета, если аукцион платный
      if (form.is_paid) {
        if (!form.ticket_price || form.ticket_price <= 0) {
          validation.ticket_price = 'Цена билета должна быть больше нуля';
          isValid = false;
        }
      }
      
      return isValid;
    };
    
    // Создание аукциона
    const createAuction = async () => {
      if (!validateForm()) {
        return;
      }
      
      loading.value = true;
      error.value = null;
      
      try {
        // Получаем ID благотворительной организации пользователя
        let charityId = null;
        if (authStore.user && authStore.user.role === 'charity') {
          try {
            const charityResponse = await authApi.getUserCharity();
            if (charityResponse.data && charityResponse.data.id) {
              charityId = charityResponse.data.id;
            }
          } catch (e) {
            console.error('Ошибка при получении charity_id:', e);
          }
        }
        
        // Если не удалось получить ID, показываем ошибку
        if (!charityId) {
          error.value = 'Не удалось определить благотворительную организацию. Убедитесь, что у вас есть права на создание аукциона.';
          loading.value = false;
          return;
        }
        
        // Формируем данные для отправки
        const formData = new FormData();
        formData.append('name', form.title);
        formData.append('description', form.description);
        formData.append('start_time', new Date(form.start_date).toISOString());
        formData.append('end_time', new Date(form.end_date).toISOString());
        
        // Добавляем ID благотворительной организации
        formData.append('charity', charityId);
        
        // Добавляем данные о платности аукциона
        formData.append('is_paid', form.is_paid);
        if (form.is_paid) {
          formData.append('ticket_price', form.ticket_price);
        }
        
        // Добавляем изображение, если оно есть
        if (imageFile.value) {
          formData.append('image', imageFile.value);
        }
        
        let result;
        
        if (isEditMode.value) {
          // Редактирование существующего аукциона
          result = await auctionsStore.updateAuction(editAuctionId.value, formData);
        } else {
          // Создание нового аукциона
          result = await auctionsStore.createAuction(formData);
        }
        
        if (result) {
          success.value = true;
          // Перенаправляем на страницу аукционов после небольшой задержки
          setTimeout(() => {
            router.push('/auctions');
          }, 3000);
        }
      } catch (err) {
        console.error('Ошибка при создании аукциона:', err);
        
        if (err.response?.data) {
          const errorData = err.response.data;
          
          // Заполняем ошибки валидации
          Object.keys(errorData).forEach(key => {
            if (key in validation) {
              validation[key] = Array.isArray(errorData[key]) 
                ? errorData[key].join(' ') 
                : errorData[key];
            }
          });
          
          // Обрабатываем общую ошибку
          if (errorData.detail || errorData.non_field_errors || (errorData.error && typeof errorData.error === 'string')) {
            error.value = errorData.detail || 
                          (Array.isArray(errorData.non_field_errors) ? errorData.non_field_errors.join(' ') : errorData.non_field_errors) ||
                          errorData.error;
          } else {
            error.value = 'Произошла ошибка при создании аукциона';
          }
        } else {
          error.value = 'Не удалось подключиться к серверу';
        }
      } finally {
        loading.value = false;
      }
    };
    
    // Возврат на предыдущую страницу
    const goBack = () => {
      router.back();
    };
    
    return {
      loading,
      error,
      success,
      form,
      validation,
      imageFile,
      imagePreview,
      imageFileName,
      handleImageUpload,
      triggerImageInput,
      removeImage,
      createAuction,
      goBack,
      isEditMode
    };
  }
}
</script>

<style scoped>
.create-auction-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 32px 24px;
}

h1 {
  margin-bottom: 24px;
  color: #333;
  text-align: center;
}

.auction-form {
  background-color: #fff;
  border-radius: 10px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  padding: 24px;
}

.form-group {
  margin-bottom: 20px;
}

.form-row {
  display: flex;
  gap: 16px;
  margin-bottom: 20px;
}

.half {
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
input[type="datetime-local"],
textarea {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #ced4da;
  border-radius: 4px;
  font-size: 16px;
  transition: border-color 0.3s;
}

input:focus,
textarea:focus {
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

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 24px;
}

.btn-primary,
.btn-secondary {
  padding: 10px 20px;
  border-radius: 4px;
  font-weight: 500;
  cursor: pointer;
  border: none;
  transition: background-color 0.3s;
}

.btn-primary {
  background-color: #007bff;
  color: white;
}

.btn-primary:hover {
  background-color: #0069d9;
}

.btn-primary:disabled {
  background-color: #6c9bd9;
  cursor: not-allowed;
}

.btn-secondary {
  background-color: #6c757d;
  color: white;
}

.btn-secondary:hover {
  background-color: #5a6268;
}

/* Стили для загрузки изображения */
.image-upload-container {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

input[type="file"] {
  display: none;
}

.upload-button {
  padding: 10px 16px;
  background-color: #f8f9fa;
  border: 1px solid #ced4da;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.upload-button:hover {
  background-color: #e2e6ea;
}

.file-name {
  font-size: 14px;
  color: #495057;
}

.image-preview-container {
  position: relative;
  margin-top: 16px;
  max-width: 300px;
}

.image-preview {
  width: 100%;
  max-height: 200px;
  border-radius: 4px;
  object-fit: cover;
  border: 1px solid #ddd;
}

.remove-image-btn {
  position: absolute;
  top: -10px;
  right: -10px;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background-color: #dc3545;
  color: white;
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  font-size: 16px;
  line-height: 1;
}

@media (max-width: 576px) {
  .create-auction-container {
    padding: 16px;
  }
  
  .form-row {
    flex-direction: column;
    gap: 20px;
  }
  
  .form-actions {
    flex-direction: column-reverse;
  }
  
  .btn-primary,
  .btn-secondary {
    width: 100%;
  }
  
  .image-upload-container {
    flex-direction: column;
    align-items: flex-start;
  }
}

.error-alert ::v-deep(.alert-message) {
  white-space: pre-line;
}

.form-notice {
  background-color: #f8f9fa;
  border-left: 4px solid #17a2b8;
  padding: 12px 16px;
  margin-bottom: 20px;
  border-radius: 4px;
}

.form-notice p {
  margin: 0;
  color: #555;
  font-size: 14px;
}

/* Стили для чекбокса */
.checkbox-container {
  display: flex;
  align-items: center;
  gap: 8px;
}

.checkbox-container input[type="checkbox"] {
  width: 16px;
  height: 16px;
}
</style> 