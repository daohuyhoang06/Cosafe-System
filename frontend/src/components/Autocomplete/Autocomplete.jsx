import { useState, useEffect, useRef } from 'react';
import { productService } from '@/services';
import './Autocomplete.css';

const Autocomplete = ({ value, onChange, onSelect, placeholder }) => {
    const [suggestions, setSuggestions] = useState([]);
    const [showSuggestions, setShowSuggestions] = useState(false);
    const [isLoading, setIsLoading] = useState(false);
    const debounceTimeout = useRef(null);
    const inputRef = useRef(null);

    useEffect(() => {
        if (debounceTimeout.current) {
            clearTimeout(debounceTimeout.current);
        }

        if (!value.trim()) {
            setSuggestions([]);
            setShowSuggestions(false);
            return;
        }

        debounceTimeout.current = setTimeout(async () => {
            setIsLoading(true);
            try {
                const data = await productService.autocomplete(value, 10);
                setSuggestions(data.products || []);
                setShowSuggestions(true);
            } catch (error) {
                console.error('Autocomplete error:', error);
                setSuggestions([]);
            } finally {
                setIsLoading(false);
            }
        }, 250);

        return () => {
            if (debounceTimeout.current) {
                clearTimeout(debounceTimeout.current);
            }
        };
    }, [value]);

    const handleSelect = (product) => {
        onSelect(product);
        setShowSuggestions(false);
    };

    const handleClickOutside = (e) => {
        if (inputRef.current && !inputRef.current.contains(e.target)) {
            setShowSuggestions(false);
        }
    };

    useEffect(() => {
        document.addEventListener('mousedown', handleClickOutside);
        return () => {
            document.removeEventListener('mousedown', handleClickOutside);
        };
    }, []);

    return (
        <div className="autocomplete-container" ref={inputRef}>
            <input
                type="text"
                value={value}
                onChange={(e) => onChange(e.target.value)}
                onFocus={() => value.trim() && suggestions.length > 0 && setShowSuggestions(true)}
                placeholder={placeholder}
                className="search-bar"
            />

            {showSuggestions && suggestions.length > 0 && (
                <div className="autocomplete-suggestions">
                    {suggestions.map((product, index) => (
                        <div
                            key={index}
                            className="suggestion-item"
                            onClick={() => handleSelect(product)}
                        >
                            <img
                                src={product.link_image || '/assets/images/product-placeholder.jpg'}
                                alt={product.name}
                                className="suggestion-img"
                            />
                            <span>{product.name}</span>
                        </div>
                    ))}
                </div>
            )}

            {showSuggestions && suggestions.length === 0 && !isLoading && value.trim() && (
                <div className="autocomplete-suggestions">
                    <div className="no-suggestion">No suggestions found.</div>
                </div>
            )}
        </div>
    );
};

export default Autocomplete;
