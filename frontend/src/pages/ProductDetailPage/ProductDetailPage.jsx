import { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { Header } from '@/components';
import { productService, nerService } from '@/services';
import './ProductDetailPage.css';

const ProductDetailPage = () => {
    const [searchParams] = useSearchParams();
    const productName = searchParams.get('name') || '';

    const [product, setProduct] = useState(null);
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        if (productName) {
            loadProductDetails();
        }
    }, [productName]);

    const loadProductDetails = async () => {
        setIsLoading(true);
        try {
            const data = await productService.getDetails(productName);
            setProduct(data);
        } catch (error) {
            console.error('Error loading product:', error);
        } finally {
            setIsLoading(false);
        }
    };

    if (isLoading) {
        return (
            <div className="product-detail-page">
                <Header />
                <div className="loading-container">Loading product details...</div>
            </div>
        );
    }

    if (!product || product.message) {
        return (
            <div className="product-detail-page">
                <Header />
                <div className="error-container">Product not found</div>
            </div>
        );
    }

    return (
        <div className="product-detail-page">
            <Header />

            <div className="product-detail-container">
                <div className="product-header">
                    <img
                        src={product.link_image || '/assets/images/product-placeholder.jpg'}
                        alt={product.name}
                        className="product-detail-img"
                    />
                    <div className="product-info">
                        <h1>{product.name}</h1>
                        <div className="score-badge">
                            <span className="score-label">Safety Score:</span>
                            <span className="score-value">{product.score}</span>
                        </div>
                    </div>
                </div>

                {product.ingredients && Object.keys(product.ingredients).length > 0 && (
                    <div className="ingredients-section">
                        <h2>Ingredients</h2>
                        <div className="ingredients-grid">
                            {Object.entries(product.ingredients).map(([name, data], index) => (
                                <div key={index} className="ingredient-item">
                                    <span className="ingredient-name">{name}</span>
                                    {data.score !== undefined && (
                                        <span className="ingredient-score">Score: {data.score}</span>
                                    )}
                                </div>
                            ))}
                        </div>
                    </div>
                )}

                {product.brand && (
                    <div className="detail-section">
                        <h3>Brand</h3>
                        <p>{product.brand}</p>
                    </div>
                )}

                {product.category && (
                    <div className="detail-section">
                        <h3>Category</h3>
                        <p>{product.category}</p>
                    </div>
                )}
            </div>
        </div>
    );
};

export default ProductDetailPage;
