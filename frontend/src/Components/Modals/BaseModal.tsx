// Third Party
import { Button, Modal } from "react-bootstrap";
import { useTranslation } from "react-i18next";

// AA Belt Radar
import { ModalSize } from "./ModalSize";

export interface ApproveData {
  title: string;
  textBody: React.ReactNode;
  buttonText?: string;
  url: string;
}

function ApproveModal({
  ApproveData,
  showModal,
  onApprove,
  setShowModal,
}: {
  ApproveData: ApproveData;
  showModal: boolean;
  onApprove: (url: string) => void;
  setShowModal: (show: boolean) => void;
}) {
  const { t } = useTranslation();
  return (
    <Modal
      show={showModal}
      size={ModalSize.large}
      onHide={() => {
        setShowModal(false);
      }}
      centered={true}
    >
      <Modal.Header closeButton>
        <Modal.Title>{ApproveData.title}</Modal.Title>
      </Modal.Header>
      <Modal.Body>
        {ApproveData.textBody}
      </Modal.Body>
      <Modal.Footer>
        <Button onClick={() => { onApprove(ApproveData.url); setShowModal(false); }}>
          {t("Approve")} {ApproveData.buttonText ?? ""}
        </Button>
        <Button onClick={() => setShowModal(false)}>
          {t("Close")}
        </Button>
      </Modal.Footer>
    </Modal>
  );
}

export default ApproveModal;
