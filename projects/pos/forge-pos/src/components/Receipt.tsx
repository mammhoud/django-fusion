import { forwardRef } from 'react';
import { useTranslation } from 'react-i18next';
import { Settings } from '../types';

interface ReceiptProps {
  products: {
    name: string;
    quantity: number;
    unit: string;
    price: number;
  }[];
  totalAmount: number;
  date: string;
  time: string;
  settings: Settings;
  receiptNumber: string;
  orderType?: string;
  deliveryTypeName?: string;
  deliveryAddress?: string;
  deliveryFee?: number;
  deliveryZoneName?: string;
  deliveryDistance?: number;
}

const Receipt = forwardRef<HTMLDivElement, ReceiptProps>(
  ({ products, totalAmount, date, time, settings, receiptNumber, orderType, deliveryTypeName, deliveryAddress, deliveryFee, deliveryZoneName, deliveryDistance }, ref) => {
    const { t } = useTranslation();
    const orderLabel = orderType ? orderType.charAt(0).toUpperCase() + orderType.slice(1) : '';
    const hasDelivery = deliveryFee && deliveryFee > 0;
    return (
      <div ref={ref} className="receipt-container">
        <div className="receipt-content bg-white text-black p-6 max-w-sm mx-auto rounded-lg">
          {/* Header */}
          <div className="text-center mb-4">
            {settings.invoice_logo && (
              <img 
                src={settings.invoice_logo} 
                alt="Business Logo" 
                className="mx-auto mb-2 max-w-[100px] max-h-[100px] object-contain"
              />
            )}
            <h2 className="text-xl font-bold mb-1">
              {settings.restaurant_name || 'Forge POS'}
            </h2>
            {settings.address && (
              <p className="text-xs text-gray-600">{settings.address}</p>
            )}
            {settings.phone && (
              <p className="text-xs text-gray-600">{t('receipt.tel')} {settings.phone}</p>
            )}
            <div className="text-xs text-gray-600 mt-2">
              <span>{t('receipt.date')} {date}</span>
              <span className="ml-4">{t('receipt.time')} {time}</span>
            </div>
            <p className="text-xs text-gray-600">{t('receipt.receiptNumber')} {receiptNumber}</p>

            {/* Order Type Badge */}
            {orderType && (
              <div className="mt-2">
                <span className={`inline-block px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider ${
                  orderType === 'delivery' ? 'bg-orange-100 text-orange-700' :
                  orderType === 'dine-in' ? 'bg-blue-100 text-blue-700' :
                  'bg-teal-100 text-teal-700'
                }`}>
                  {orderLabel}
                </span>
                {orderType === 'dine-in' && deliveryTypeName && (
                  <span className="ml-1 inline-block px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-blue-100 text-blue-700">
                    {deliveryTypeName}
                  </span>
                )}
                {orderType === 'delivery' && deliveryTypeName && (
                  <span className="ml-1 inline-block px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-orange-100 text-orange-700">
                    {deliveryTypeName}
                  </span>
                )}
              </div>
            )}
            {orderType === 'delivery' && deliveryAddress && (
              <p className="text-[10px] text-gray-500 mt-1">
                {deliveryAddress}
              </p>
            )}
            {orderType === 'delivery' && deliveryZoneName && (
              <p className="text-[10px] text-gray-500 mt-0.5">
                Zone: {deliveryZoneName}{deliveryDistance ? ` — ${deliveryDistance} km` : ''}
              </p>
            )}
          </div>

          {/* Separator */}
          <div className="border-t-2 border-dashed border-gray-400 my-3" />

          {/* Items Header */}
          <div className="grid grid-cols-3 text-xs font-bold mb-2">
            <div>{t('receipt.itemHeader')}</div>
            <div className="text-center">{t('receipt.qtyHeader')}</div>
            <div className="text-right">{t('receipt.priceHeader')}</div>
          </div>

          {/* Items */}
          <div className="space-y-1 mb-3">
            {products.map((product, index) => (
              <div key={index} className="grid grid-cols-3 text-xs">
                <div className="truncate">{product.name}</div>
                <div className="text-center">
                  {product.quantity} {product.unit}
                </div>
                <div className="text-right">
                  {settings.currency} {product.price.toFixed(2)}
                </div>
              </div>
            ))}
          </div>

          {/* Separator */}
          <div className="border-t-2 border-dashed border-gray-400 my-3" />

          {/* Totals with delivery fee breakdown */}
          <div className="space-y-1 mb-4">
            <div className="flex justify-between items-center text-xs text-gray-600">
              <span>{t('receipt.subtotal', 'Subtotal')}</span>
              <span>{settings.currency} {hasDelivery ? (totalAmount - deliveryFee!).toFixed(2) : totalAmount.toFixed(2)}</span>
            </div>
            {hasDelivery && (
              <div className="flex justify-between items-center text-xs text-orange-600">
                <span>{t('sale.deliveryFee', 'Delivery Fee')}</span>
                <span>{settings.currency} {deliveryFee!.toFixed(2)}</span>
              </div>
            )}
            <div className="flex justify-between items-center font-bold text-base border-t border-dashed border-gray-400 pt-1">
              <span>{t('receipt.totalLabel')}</span>
              <span>{settings.currency} {hasDelivery ? totalAmount.toFixed(2) : totalAmount.toFixed(2)}</span>
            </div>
          </div>

          {/* Footer */}
          {settings.receipt_footer && (
            <>
              <div className="border-t-2 border-dashed border-gray-400 my-3" />
              <div className="text-center text-xs text-gray-600">
                {settings.receipt_footer}
              </div>
            </>
          )}
        </div>

        {/* Print styles */}
        <style dangerouslySetInnerHTML={{__html: `
          @media print {
            @page {
              size: 80mm auto;
              margin: 0;
            }
            
            * {
              box-sizing: border-box;
            }
            
            html, body {
              width: 80mm !important;
              height: auto !important;
              margin: 0 !important;
              padding: 0 !important;
              background: white !important;
              overflow: visible !important;
            }
            
            /* Hide absolutely everything first */
            body * {
              display: none !important;
            }
            
            /* Only show receipt container and its children */
            .receipt-container {
              display: block !important;
              position: static !important;
              visibility: visible !important;
              width: 80mm !important;
              height: auto !important;
              margin: 0 !important;
              padding: 0 !important;
              background: white !important;
            }
            
            .receipt-container * {
              display: revert !important;
              visibility: visible !important;
            }
            
            .receipt-content {
              box-shadow: none !important;
              border-radius: 0 !important;
              max-width: 80mm !important;
              width: 80mm !important;
              margin: 0 !important;
              padding: 5mm !important;
              background: white !important;
            }
          }
        `}} />
      </div>
    );
  }
);

Receipt.displayName = 'Receipt';

export default Receipt;

