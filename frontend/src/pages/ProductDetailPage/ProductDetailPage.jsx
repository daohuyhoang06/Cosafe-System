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
                            <span className={`score-value score-${product.score}`}>{product.score}</span>
                            <span className="score-description">
                                {product.score <= 2 ? '(Very Safe)' :
                                    product.score <= 4 ? '(Safe)' :
                                        product.score <= 6 ? '(Moderate)' :
                                            '(High Concern)'}
                            </span>
                        </div>

                        {product.product_url && (
                            <a
                                href={product.product_url}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="product-ewg-link"
                            >
                                📊 View Full EWG Report →
                            </a>
                        )}

                        {product.ingredient_concerns && (
                            <div className="concerns-box">
                                <h3>Ingredient Concerns</h3>
                                <div className="concerns-grid">
                                    {product.ingredient_concerns.cancer && (
                                        <div className="concern-item">
                                            <span className="concern-label">Cancer:</span>
                                            <span className={`concern-value ${product.ingredient_concerns.cancer.toLowerCase()}`}>
                                                {product.ingredient_concerns.cancer}
                                            </span>
                                        </div>
                                    )}
                                    {product.ingredient_concerns.allergies_immunotoxicity && (
                                        <div className="concern-item">
                                            <span className="concern-label">Allergies & Immunotoxicity:</span>
                                            <span className={`concern-value ${product.ingredient_concerns.allergies_immunotoxicity.toLowerCase()}`}>
                                                {product.ingredient_concerns.allergies_immunotoxicity}
                                            </span>
                                        </div>
                                    )}
                                    {product.ingredient_concerns.developmental_reproductive_toxicity && (
                                        <div className="concern-item">
                                            <span className="concern-label">Developmental & Reproductive:</span>
                                            <span className={`concern-value ${product.ingredient_concerns.developmental_reproductive_toxicity.toLowerCase()}`}>
                                                {product.ingredient_concerns.developmental_reproductive_toxicity}
                                            </span>
                                        </div>
                                    )}
                                    {product.ingredient_concerns.use_restrictions && (
                                        <div className="concern-item">
                                            <span className="concern-label">Use Restrictions:</span>
                                            <span className={`concern-value ${product.ingredient_concerns.use_restrictions.toLowerCase()}`}>
                                                {product.ingredient_concerns.use_restrictions}
                                            </span>
                                        </div>
                                    )}
                                </div>
                            </div>
                        )}
                    </div>
                </div>

                {product.ingredients && Array.isArray(product.ingredients) && product.ingredients.length > 0 && (
                    <div className="ingredients-section">
                        <h2>Ingredients ({product.ingredients.length})</h2>
                        <div className="ingredients-list">
                            {product.ingredients.map((ingredient, index) => (
                                <div key={index} className="ingredient-item">
                                    <div className="ingredient-info">
                                        <span className="ingredient-name">{ingredient.name}</span>
                                        <span className={`ingredient-score score-${ingredient.score}`}>
                                            Score: {ingredient.score}
                                        </span>
                                    </div>
                                    {ingredient.link && (
                                        <a
                                            href={ingredient.link}
                                            target="_blank"
                                            rel="noopener noreferrer"
                                            className="ingredient-link"
                                        >
                                            View EWG Details →
                                        </a>
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
