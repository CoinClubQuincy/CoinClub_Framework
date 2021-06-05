//
//  SerialViewController.swift
//  HM10 Serial
//
//  Created by Alex on 10-08-15.
//  Copyright (c) 2015 Balancing Rock. All rights reserved.
//

import UIKit
import CoreBluetooth
import QuartzCore
import LocalAuthentication
import TOPasscodeViewController

/// The option to add a \n or \r or \r\n to the end of the send message
enum MessageOption: Int {
    case noLineEnding,
    newline,
    carriageReturn,
    carriageReturnAndNewline
}

/// The option to add a \n to the end of the received message (to make it more readable)
enum ReceivedMessageOption: Int {
    case none,
    newline
}

final class SerialViewController: UIViewController, UITextFieldDelegate, BluetoothSerialDelegate, UITableViewDelegate, UITableViewDataSource, TOPasscodeViewControllerDelegate, TOPasscodeSettingsViewControllerDelegate, UtilityDelegate, UIScrollViewDelegate {
    
    //MARK: IBOutlets
    
    @IBOutlet weak var tableView: UITableView!
    @IBOutlet weak var barButton: UIBarButtonItem!
    @IBOutlet weak var navItem: UINavigationItem!
    @IBOutlet weak var authenticateView: UIView!
    @IBOutlet weak var authenticateButton: UIButton!
    
    var cardList: [CardModel] = []
    var message: String = ""
    let commandArray: [String] = ["A", "B", "C", "D", "E","F"]
    var selectedIndexes =  [Int]()
    
    let utility: Utility = Utility()
    
    //MARK: Functions
    
    override func viewDidLoad() {
        super.viewDidLoad()
        
        // init serial
        
        self.utility.delegate = self
        NotificationCenter.default.addObserver(self, selector: #selector(SerialViewController.reloadView), name: NSNotification.Name(rawValue: "reloadStartViewController"), object: nil)
        self.authenticateView.isHidden = false
        
        NotificationCenter.default.addObserver(self, selector: #selector(sendTextDismiss(_:)), name: NotificationCenterHelper.SendDimissView, object: nil)
        NotificationCenter.default.addObserver(self, selector: #selector(reloadViewData(_:)), name: NotificationCenterHelper.reloadViewData, object: nil)
        serial = BluetoothSerial(delegate: self)
        reloadView()
    }
    
//    deinit {
//        NotificationCenter.default.removeObserver(self)
//    }
//
    @objc func sendTextDismiss(_ notification: Notification) {
        self.sendText(text: "G")
    }
    
    @objc func reloadViewData(_ notification: Notification) {
        self.cardList = CoreDataHelper.getCards()
        self.tableView.reloadData()
        AppData.sharedInstance.homeViewController = self
    }
    
    override func viewWillAppear(_ animated: Bool) {
        self.cardList = CoreDataHelper.getCards()
        self.tableView.reloadData()
        AppData.sharedInstance.homeViewController = self
    }
    override func viewWillDisappear(_ animated: Bool) {
        AppData.sharedInstance.homeViewController = nil
    }
    override func viewDidAppear(_ animated: Bool) {
        if (AppData.sharedInstance.isPhoneUnlocked) {
            self.authenticateView.isHidden = true
            return
        }
        self.authenticateView.isHidden = false
        self.utility.useTouchID(description: "Please Authenticate to continue", viewController: self)
    }
    
    @objc func reloadView() {
        // in case we're the visible view again
        serial.delegate = self
        
        if serial.isReady {
            navItem.title = serial.connectedPeripheral!.name
            barButton.title = "Disconnect"
            barButton.tintColor = UIColor.red
            barButton.isEnabled = true
        } else if serial.centralManager.state == .poweredOn {
            navItem.title = "Bluetooth Serial"
            barButton.title = "Connect"
            barButton.tintColor = UIColor.black
            barButton.isEnabled = true
            Utility.showAlert(AppName, "Please Connect with Blutooth", viewController: self)
        } else {
            navItem.title = "Bluetooth Serial"
            barButton.title = "Connect"
            barButton.tintColor = UIColor.black
            barButton.isEnabled = true
            Utility.showAlert(AppName, "Please Connect with Blutooth", viewController: self)
        }
    }
    
    func serialDidDisconnect(_ peripheral: CBPeripheral, error: NSError?) {
        reloadView()
        let hud = MBProgressHUD.showAdded(to: view, animated: true)
        hud?.mode = MBProgressHUDMode.text
        hud?.labelText = "Disconnected"
        hud?.hide(true, afterDelay: 1.0)
    }
    
    func serialDidChangeState() {
        reloadView()
        if serial.centralManager.state != .poweredOn {
            let hud = MBProgressHUD.showAdded(to: view, animated: true)
            hud?.mode = MBProgressHUDMode.text
            hud?.labelText = "Bluetooth turned off"
            hud?.hide(true, afterDelay: 1.0)
        }
    }
    
    //MARK: IBActions
    
    @IBAction func barButtonPressed(_ sender: AnyObject) {
        if serial.connectedPeripheral == nil {
            performSegue(withIdentifier: "ShowScanner", sender: self)
        } else {
            serial.disconnect()
            reloadView()
        }
    }
    
    func sendText(text: String) {
        if !serial.isReady {
            let alert = UIAlertController(title: "Not connected", message: "What am I supposed to send this to?", preferredStyle: .alert)
            alert.addAction(UIAlertAction(title: "Dismiss", style: UIAlertActionStyle.default, handler: { action -> Void in self.dismiss(animated: true, completion: nil) }))
            present(alert, animated: true, completion: nil)
        } else {
            let pref = UserDefaults.standard.integer(forKey: MessageOptionKey)
            var msg = text
            switch pref {
            case MessageOption.newline.rawValue:
                msg += "\n"
            case MessageOption.carriageReturn.rawValue:
                msg += "\r"
            case MessageOption.carriageReturnAndNewline.rawValue:
                msg += "\r\n"
            default:
                msg += ""
            }
            AppData.sharedInstance.senderText = msg
            serial.sendMessageToDevice(msg)
        }
    }
    
    //MARK: - Tableview Delegate and Datasource
    
    func tableView(_ tableView: UITableView, numberOfRowsInSection section: Int) -> Int {
        return self.cardList.count
    }
    
    func tableView(_ tableView: UITableView, cellForRowAt indexPath: IndexPath) -> UITableViewCell {
        
        let cell = tableView.dequeueReusableCell(withIdentifier: "Cell", for: indexPath) as! SerialTableViewCell
        
        let cardData = self.cardList[indexPath.row]
        cell.cardName.setTitle(cardData.cardName , for: .normal)
        cell.cardName.backgroundColor = UIColor(hexString: cardData.cardColor!)
        cell.cardImage.isHidden = false
        if cardData.cardImage != nil {
            cell.cardImage.image = UIImage(data:cardData.cardImage!)
            cell.cardImage.isHidden = false
        } else {
            cell.cardImage.isHidden = true
        }
        cell.cardName.accessibilityHint = "A\(indexPath.row)"
        if self.message != "" {
            self.reciveData(button: cell.cardName)
        }
        cell.cardName.isEnabled = true
        cell.cardName.tag = indexPath.row
        for recognizer in cell.cardName.gestureRecognizers ?? [] {
            cell.cardName.removeGestureRecognizer(recognizer)
        }
        cell.cardName.addTarget(self, action: #selector(self.singleButtonCardTouchAction(_:)), for: .touchUpInside)
        let longGesture = UILongPressGestureRecognizer(target: self, action: #selector(self.longButtonCardTouchAction(_:)))
        cell.cardName.isUserInteractionEnabled = true
        cell.cardName.addGestureRecognizer(longGesture)
        
        return cell
    }
    
    func tableView(_ tableView: UITableView, heightForRowAt indexPath: IndexPath) -> CGFloat {
        return 80
    }
    
    //MARK: Button Action
    
    @objc func longButtonCardTouchAction(_ sender: UITapGestureRecognizer) {
        let cell = tableView.cellForRow(at: IndexPath(row: sender.view?.tag ?? 0, section: 0)) as! SerialTableViewCell
        cell.cardName.isEnabled = true
        
//        if self.cardList[sender.view!.tag].cardName != "Empty" {
        if self.cardList[sender.view!.tag].isUpdate! {
            let controller = StoryBoardHelper.getAddCardViewController()
            controller.isUpdate = true
            controller.cardModel = self.cardList[sender.view!.tag]
            controller.cc_setZoomTransition(originalView: cell.cardName)
            self.present(controller, animated: true, completion: nil)
        }
    }
    
    @objc func singleButtonCardTouchAction(_ sender: UIButton) {
        
        let cell = tableView.cellForRow(at: IndexPath(row: sender.tag, section: 0)) as! SerialTableViewCell
        cell.cardName.isEnabled = true
        
//        if sender.titleLabel?.text == "Empty" {
        if sender.titleLabel?.text == "Press to add slot" {
            let controller = StoryBoardHelper.getAddCardViewController()
            controller.isUpdate = false
            controller.cardModel = self.cardList[sender.tag]
            AppData.sharedInstance.selectedImage = cell.cardImage.image
            AppData.sharedInstance.selectedColor = cell.cardName.backgroundColor
            controller.cc_setZoomTransition(originalView: cell.cardName)
            self.present(controller, animated: true, completion: nil)
        } else {
            if serial.isReady {
                cell.cardName.isEnabled = true
            } /*else if serial.centralManager.state == .poweredOn {
             cell.cardName.isEnabled = false
             } else {
             cell.cardName.isEnabled = false
             }*/
            
            if barButton.title != "Connect" {
                
                let controller = self.storyboard?.instantiateViewController(withIdentifier: "SerialDetailViewController") as! SerialDetailViewController
                controller.cardModel = self.cardList[sender.tag]
                controller.cc_setZoomTransition(originalView: cell.cardName)
                self.present(controller, animated: true, completion: nil)
                
                var text: String?
                if sender.titleLabel?.text != "Press to add slot" {
                    text = commandArray[sender.tag]
                    //                    sender.backgroundColor = UIColor.white
                    self.selectedIndexes.append(sender.tag)
                    self.sendText(text: text!)
                }
            } else {
                Utility.showAlert("WallApp", "Connect with Bluetooth", viewController: self)
            }
        }
    }
    
    //MARK: BluetoothSerialDelegate
    
    func serialDidReceiveString(_ message: String) {
        print(message)
        self.message = message
        AppData.sharedInstance.reciverText = self.message
        self.tableView.reloadData()
    }
    
    func reciveData(button: UIButton) {
        if self.message.lowercased() == button.accessibilityHint?.lowercased() && selectedIndexes.contains(button.tag) {
            button.backgroundColor =  button.backgroundColor?.withAlphaComponent(0.3)
            button.isEnabled = false
        }
        else if selectedIndexes.contains(button.tag) {
            //            button.backgroundColor =  UIColor.white
            button.isEnabled = true
        }
    }
    // MARK: - TOPasscode View Controller Delegate Event
    func didTapCancel(in passcodeViewController: TOPasscodeViewController) {
    }
    
    func passcodeViewController(_ passcodeViewController: TOPasscodeViewController, isCorrectCode code: String) -> Bool {
        AppData.sharedInstance.isPhoneUnlocked = code == Utility.getPasscode()
        return AppData.sharedInstance.isPhoneUnlocked
    }
    
    func passcodeSettingsViewController(_ passcodeSettingsViewController: TOPasscodeSettingsViewController, didAttemptCurrentPasscode passcode: String) -> Bool {
        return true
    }
    
    func passcodeSettingsViewController(_ passcodeSettingsViewController: TOPasscodeSettingsViewController, didChangeToNewPasscode passcode: String, of type: TOPasscodeType) {
        print("New Passcode: \(passcode)")
        Utility.savePasscode(passcode: passcode)
        Utility.savePasscodeType(passcode: type.rawValue)
        passcodeSettingsViewController.dismiss(animated: true, completion: nil)
    }
    
    // MARK: - Utility Delegate
    func touchIdLoginResponse(success: Bool, message: String?, error: Error?) {
        if(!success) {
            if #available(iOS 11.0, *) {
                switch (error! as NSError).code {
                case LAError.biometryNotEnrolled.rawValue, LAError.passcodeNotSet.rawValue, LAError.biometryNotAvailable.rawValue:
                    self.handleBiomatricIdError()
                    break;
                default:
                    break;
                }
            } else {
                switch (error! as NSError).code {
                case LAError.touchIDNotEnrolled.rawValue, LAError.passcodeNotSet.rawValue, LAError.touchIDNotAvailable.rawValue:
                    self.handleBiomatricIdError()
                    break;
                default:
                    break;
                }
                // Fallback on earlier versions
            }
        }
        else {
            self.authenticateView.isHidden = true
            AppData.sharedInstance.isPhoneUnlocked = true
        }
    }
    
    func handleBiomatricIdError() {
        let type = TOPasscodeType(rawValue: Utility.getPasscodeType())!
        if(Utility.getPasscode() == "") {
            let settingsController = TOPasscodeSettingsViewController(style: TOPasscodeSettingsViewStyle.light)
            settingsController.passcodeType = type;
            settingsController.delegate = self;
            settingsController.requireCurrentPasscode = false;
            self.present(settingsController, animated: true, completion: nil)
        }
        else {
            let passcodeViewController = TOPasscodeViewController(style: TOPasscodeViewStyle.opaqueLight, passcodeType: type)
            passcodeViewController.delegate = self
            passcodeViewController.cancelButton.isHidden = true
            self.present(passcodeViewController, animated: true, completion: nil)
        }
    }
    @IBAction func authenticateButtonTapped(_ sender: Any) {
        self.utility.useTouchID(description: "Please Authenticate to continue", viewController: self)
    }
}
