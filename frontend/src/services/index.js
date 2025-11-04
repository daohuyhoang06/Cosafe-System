import api from './api';

export const productService = {
  // Get product safety info
  getSafety: async (name) => {
    const response = await api.post('/api/products/safety', { name });
    return response.data;
  },

  // Get all product details
  getDetails: async (name) => {
    const response = await api.post('/api/products/get-all', { name });
    return response.data;
  },

  // Search products
  search: async (keyword, page = 1, size = 20, sort = 'default') => {
    const response = await api.post('/api/products/search', {
      keyword,
      page,
      size,
      sort,
    });
    return response.data;
  },

  // Autocomplete
  autocomplete: async (keyword, size = 10) => {
    const response = await api.post('/api/products/autocomplete', {
      keyword,
      size,
    });
    return response.data;
  },
};

export const nerService = {
  // Analyze ingredients
  analyzeIngredients: async (content) => {
    const response = await api.post('/api/ner/name-entity-recognition', {
      content,
    });
    return response.data;
  },
};

export const imageService = {
  // Process image
  processImage: async (file) => {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await api.post('/api/image/image-process', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },
};

export const emailService = {
  // Send guide email
  sendGuide: async (email) => {
    const response = await api.post('/api/email/send-guide-email', { email });
    return response.data;
  },
};
