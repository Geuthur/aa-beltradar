// Third Party
import Form from 'react-bootstrap/Form';
import { useTranslation } from 'react-i18next';

// AA Belt Radar
import {
    ALL_BELT_SIZES,
    BELT_SIZE_CHOICES_BY_TYPE,
    BELT_TYPE_OPTIONS,
} from '@/Components/Forms/validation';

type FormData = Record<string, string | boolean>;

interface CreateBeltTimerFormProps {
    formData: FormData;
    onChange: (data: FormData) => void;
    validated?: boolean;
}

/**
 * Renders the form for creating a belt timer with dynamic size choices.
 * @param formData - The current form data.
 * @param onChange - Callback function to handle form data changes.
 * @param validated - Indicates whether the form has been validated.
 * @returns The JSX element for the create belt timer form.
 */
export default function CreateBeltTimerForm({
    formData,
    onChange,
    validated = false,
}: CreateBeltTimerFormProps) {
    const { t } = useTranslation();

    const selectedType = (formData.belt_type as string) ?? '';
    const availableSizes = selectedType
        ? (BELT_SIZE_CHOICES_BY_TYPE[selectedType] ?? ALL_BELT_SIZES)
        : ALL_BELT_SIZES;

    const handleTypeChange = (newType: string) => {
        const validSizes = newType
            ? (BELT_SIZE_CHOICES_BY_TYPE[newType] ?? ALL_BELT_SIZES)
            : ALL_BELT_SIZES;

        const currentSize = (formData.belt_size as string) ?? '';
        const isCurrentSizeValid = validSizes.some((size) => size.value === currentSize);
        const newSize = isCurrentSizeValid ? currentSize : (validSizes[0]?.value ?? '');

        onChange({
            ...formData,
            belt_type: newType,
            belt_size: newSize,
        });
    };

    return (
        <Form noValidate className={validated ? 'was-validated' : ''}>
            <p className="text-muted mb-3">
                {t("Note: Only add a Timer if you have finished the belt. The Timer starts immediately.")}
            </p>

            <Form.Group controlId="belt_id" className="mb-3">
                <Form.Label>{t("Belt ID")}:</Form.Label>
                <Form.Control
                    type="text"
                    name="belt_id"
                    maxLength={7}
                    required
                    value={(formData.belt_id as string) ?? ''}
                    onChange={(e) => onChange({ ...formData, belt_id: e.target.value })}
                />
                <Form.Text className="text-muted d-block">
                    {t("The unique identifier for this belt timer.")}
                </Form.Text>
                <Form.Control.Feedback type="invalid">
                    {t("Belt ID is required (max 7 characters).")}
                </Form.Control.Feedback>
            </Form.Group>

            <Form.Group controlId="belt_name" className="mb-3">
                <Form.Label>{t("Belt Name")}:</Form.Label>
                <Form.Control
                    type="text"
                    name="belt_name"
                    maxLength={100}
                    required
                    value={(formData.belt_name as string) ?? ''}
                    onChange={(e) => onChange({ ...formData, belt_name: e.target.value })}
                />
                <Form.Text className="text-muted d-block">
                    {t("The name of the belt.")}
                </Form.Text>
                <Form.Control.Feedback type="invalid">
                    {t("Belt Name is required.")}
                </Form.Control.Feedback>
            </Form.Group>

            <Form.Group controlId="belt_type" className="mb-3">
                <Form.Label>{t("Belt Type")}:</Form.Label>
                <Form.Select
                    name="belt_type"
                    required
                    value={selectedType}
                    onChange={(e) => handleTypeChange(e.target.value)}
                >
                    <option value="">{t("Select Belt Type...")}</option>
                    {BELT_TYPE_OPTIONS.map((type) => (
                        <option key={type.value} value={type.value}>
                            {t(type.label)}
                        </option>
                    ))}
                </Form.Select>
                <Form.Text className="text-muted d-block">
                    {t("The type of belt.")}
                </Form.Text>
                <Form.Control.Feedback type="invalid">
                    {t("Please select a belt type.")}
                </Form.Control.Feedback>
            </Form.Group>

            <Form.Group controlId="belt_size" className="mb-3">
                <Form.Label>{t("Belt Size")}:</Form.Label>
                <Form.Select
                    name="belt_size"
                    required
                    value={(formData.belt_size as string) ?? ''}
                    onChange={(e) => onChange({ ...formData, belt_size: e.target.value })}
                >
                    <option value="">{t("Select Belt Size...")}</option>
                    {availableSizes.map((size) => (
                        <option key={size.value} value={size.value}>
                            {t(size.label)}
                        </option>
                    ))}
                </Form.Select>
                <Form.Text className="text-muted d-block">
                    {t("The size of the belt.")}
                </Form.Text>
                <Form.Control.Feedback type="invalid">
                    {t("Please select a belt size.")}
                </Form.Control.Feedback>
            </Form.Group>

            <Form.Group controlId="is_public" className="mb-3">
                <Form.Check
                    type="checkbox"
                    name="is_public"
                    label={t("Public")}
                    checked={(formData.is_public as boolean) ?? false}
                    onChange={(e) => onChange({ ...formData, is_public: e.target.checked })}
                />
                <Form.Text className="text-muted d-block">
                    {t("If checked, this belt timer will be visible to other users. Otherwise, it will be private.")}
                </Form.Text>
            </Form.Group>
        </Form>
    );
}
